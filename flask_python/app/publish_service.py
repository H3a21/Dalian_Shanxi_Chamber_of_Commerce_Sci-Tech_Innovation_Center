"""
成果和需求发布服务类
处理表单数据到MongoDB的转换和存储
"""
from datetime import datetime
from .mongo_models import Achievement, Requirement, Expert, Partner, Cooperation
from .models import User
import random
import os
import shutil


class PublishService:
    """发布服务类"""

    @staticmethod
    def _safe_sort_key(obj):
        """安全获取 created_at 用于排序，处理 str/datetime 混合类型"""
        val = getattr(obj, 'created_at', None)
        if val is None:
            return datetime.min
        if isinstance(val, datetime):
            return val
        if isinstance(val, str):
            try:
                return datetime.fromisoformat(val)
            except (ValueError, TypeError):
                return datetime.min
        return datetime.min

    @staticmethod
    def _generate_achievement_code():
        """生成成果编号，格式: CG + 年份 + 4位序号，如 CG2025001"""
        current_year = datetime.now().year
        prefix = f"CG{current_year}"

        try:
            # 查询当前年份的所有成果编号
            achievements = Achievement.find()
            max_sequence = 0

            for achievement in achievements:
                if achievement.achievement_code and achievement.achievement_code.startswith(prefix):
                    try:
                        # 提取序号部分（CG2025001 -> 001）
                        sequence_str = achievement.achievement_code[len(prefix):]
                        sequence = int(sequence_str)
                        if sequence > max_sequence:
                            max_sequence = sequence
                    except (ValueError, IndexError):
                        continue

            # 序号从1开始
            next_sequence = max_sequence + 1
            # 限制4位序号，如果超过9999则重新开始（极不可能）
            if next_sequence > 9999:
                next_sequence = 1

            return f"{prefix}{next_sequence:04d}"
        except Exception as e:
            # 如果查询失败，回退到随机数（不应该发生）
            print(f"[WARN] 查询成果编号失败: {e}, 使用随机数")
            sequence = random.randint(1, 9999)
            return f"CG{current_year}{sequence:04d}"

    @staticmethod
    def _generate_demand_code():
        """生成需求编号，格式: XQ + 年份 + 4位序号，如 XQ2025001"""
        current_year = datetime.now().year
        prefix = f"XQ{current_year}"

        try:
            # 查询当前年份的所有需求编号
            requirements = Requirement.find()
            max_sequence = 0

            for requirement in requirements:
                if requirement.demand_code and requirement.demand_code.startswith(prefix):
                    try:
                        # 提取序号部分（XQ2025001 -> 001）
                        sequence_str = requirement.demand_code[len(prefix):]
                        sequence = int(sequence_str)
                        if sequence > max_sequence:
                            max_sequence = sequence
                    except (ValueError, IndexError):
                        continue

            # 序号从1开始
            next_sequence = max_sequence + 1
            # 限制4位序号，如果超过9999则重新开始（极不可能）
            if next_sequence > 9999:
                next_sequence = 1

            return f"{prefix}{next_sequence:04d}"
        except Exception as e:
            # 如果查询失败，回退到随机数（不应该发生）
            print(f"[WARN] 查询需求编号失败: {e}, 使用随机数")
            sequence = random.randint(1, 9999)
            return f"XQ{current_year}{sequence:04d}"

    @staticmethod
    def create_achievement(user_id, form_data):
        """
        创建成果记录

        Args:
            user_id: 提交用户ID
            form_data: 前端表单数据（字典）

        Returns:
            创建的Achievement对象
        """
        # 数据转换：前端字段名 -> 后端模型字段名
        # 处理转化方式，确保是数组
        transform_types = form_data.get('transformTypes', [])
        # 如果transformTypes是字符串，尝试按逗号分割；如果是单个值，放入数组
        if isinstance(transform_types, str):
            if transform_types.strip():
                transform_types = [item.strip() for item in transform_types.split(',')]
            else:
                transform_types = []
        elif not isinstance(transform_types, list):
            # 如果不是列表，则转为列表
            transform_types = [transform_types] if transform_types is not None else []

        # 从转化方式中过滤掉"其他"选项，因为"其他"的具体内容存储在transfer_methods_other字段中
        transform_types_without_other = [item for item in transform_types if item != '其他']

        achievement_data = {
            'user_id': user_id,
            'achievement_name': form_data.get('name', ''),
            'owner': form_data.get('holder', ''),
            'province': form_data.get('province', ''),
            'city': form_data.get('city', ''),
            'tech_fields': [] if form_data.get('techField') == '其他' else ([form_data.get('techField', '')] if form_data.get('techField') else []),
            'tech_fields_other': form_data.get('techFieldOther', ''),
            'tech_maturity': form_data.get('maturity', ''),
            'transfer_methods': transform_types_without_other,
            'transfer_methods_other': form_data.get('transformOther', ''),
            'summary': form_data.get('summary', ''),
            'innovation_level': form_data.get('innovationLevel', ''),
            'advantages': form_data.get('advantages', ''),
            'core_indicators': form_data.get('techIndicators', ''),
            'intellectual_property': form_data.get('intellectualProperty', ''),
            'status': 'pending' , # 默认待审核
            'is_display': False
        }
        # 调试：打印接收到的转化方式数据
        print(f"[DEBUG] create_achievement: transformTypes raw = {form_data.get('transformTypes')}, type = {type(form_data.get('transformTypes'))}")
        print(f"[DEBUG] create_achievement: transfer_methods processed = {achievement_data['transfer_methods']}, type = {type(achievement_data['transfer_methods'])}")

        # 生成成果编号
        achievement_data['achievement_code'] = PublishService._generate_achievement_code()

        # 处理地区信息
        if achievement_data['province'] or achievement_data['city']:
            achievement_data['region'] = {
                'province': achievement_data.pop('province', ''),
                'city': achievement_data.pop('city', '')
            }

        # 处理转化偏好 - 根据合作方式偏好（单选）设置enabled，参数只在对应偏好选中时保存
        cooperation_pref = form_data.get('cooperationPref', '')
        transfer_preference = {
            'tech_transfer': {
                'enabled': cooperation_pref == '技术转让',
                'expected_fee': float(form_data.get('transferFee', 0)) if cooperation_pref == '技术转让' and form_data.get('transferFee') else 0
            },
            'tech_license': {
                'enabled': cooperation_pref == '技术许可',
                'type': form_data.get('licenseType', '') if cooperation_pref == '技术许可' else ''
            },
            'tech_investment': {
                'enabled': cooperation_pref == '技术入股',
                'valuation': float(form_data.get('equityValue', 0)) if cooperation_pref == '技术入股' and form_data.get('equityValue') else 0,
                'share_ratio': float(form_data.get('equityPercent', 0)) if cooperation_pref == '技术入股' and form_data.get('equityPercent') else 0
            },
            'cooperation_dev': cooperation_pref == '合作开发',
            'other': form_data.get('cooperationOther', '') if cooperation_pref == '其他' else '',
            'preferred_method': cooperation_pref,  # 合作方式偏好（单选）
            'expected_complete_date': {'year': 0, 'month': 0}  # 暂时简化
        }

        # 处理期望完成日期
        expect_date = form_data.get('expectDate')
        if expect_date:
            try:
                # 支持多种日期格式：Date对象、datetime对象、字符串'YYYY-MM'等
                date_obj = None
                if isinstance(expect_date, datetime):
                    date_obj = expect_date
                elif isinstance(expect_date, str):
                    # 尝试解析字符串格式 'YYYY-MM' 或 'YYYY-MM-DD'
                    if len(expect_date) >= 7 and expect_date[4] == '-':
                        date_obj = datetime.strptime(expect_date[:7], '%Y-%m')
                    else:
                        # 其他格式尝试
                        date_obj = datetime.fromisoformat(expect_date.replace('Z', '+00:00'))
                elif hasattr(expect_date, 'year') and hasattr(expect_date, 'month'):
                    # 假设是类似date的对象
                    date_obj = datetime(expect_date.year, expect_date.month, 1)
                else:
                    # 尝试转换为datetime（例如JavaScript时间戳）
                    date_obj = datetime.fromtimestamp(expect_date / 1000)

                transfer_preference['expected_complete_date'] = {
                    'year': date_obj.year,
                    'month': date_obj.month
                }
            except Exception as e:
                print(f"[WARN] 期望转化日期解析失败: {e}, 日期值: {expect_date}")
                pass

        achievement_data['transfer_preference'] = transfer_preference

        # 调试：打印最终保存的数据
        print(f"[DEBUG] create_achievement: 最终 achievement_data['transfer_methods'] = {achievement_data['transfer_methods']}")
        print(f"[DEBUG] create_achievement: 最终 achievement_data keys = {list(achievement_data.keys())}")

        # 创建并保存成果
        achievement = Achievement(**achievement_data)
        success = achievement.save()

        if success:
            print(f"[INFO] 成果创建成功: ID={achievement._id}, 编号={achievement.achievement_code}")
            return achievement
        else:
            print(f"[ERROR] 成果保存失败")
            return None

    @staticmethod
    def create_requirement(user_id, form_data):
        """
        创建需求记录

        Args:
            user_id: 提交用户ID
            form_data: 前端表单数据（字典）

        Returns:
            创建的Requirement对象
        """
        # 数据转换：前端字段名 -> 后端模型字段名
        requirement_data = {
            'user_id': user_id,
            'company_name': form_data.get('companyName', ''),
            'demand_name': form_data.get('demandName', ''),
            'province': form_data.get('province', ''),
            'city': form_data.get('city', ''),
            'tech_fields': form_data.get('tech_fields', []),
            'tech_fields_other': '',
            'demand_types': [] if form_data.get('demandType') == '其他' else ([form_data.get('demandType', '')] if form_data.get('demandType') else []),
            'demand_types_other': form_data.get('demandTypeOther', ''),
            'overview': form_data.get('description', ''),
            'target_problems': form_data.get('expectedProblem', ''),
            'status': 'pending' , # 默认待审核
            'is_display': False,
            'match_status': '待对接'
        }

        # 处理预算和单位转换（存储单位为万元，与规范示例一致）
        budget = form_data.get('budget')
        budget_unit = form_data.get('budgetUnit', '万元')

        if budget:
            try:
                budget_value = float(budget)
                # 转换为万元
                if budget_unit == '元':
                    budget_value = budget_value / 10000
                elif budget_unit == '百万元':
                    budget_value = budget_value * 100
                elif budget_unit == '亿元':
                    budget_value = budget_value * 10000
                # 万元保持不变
                requirement_data['budget'] = budget_value
            except (ValueError, TypeError):
                requirement_data['budget'] = 0
        else:
            requirement_data['budget'] = 0

        # 生成需求编号
        requirement_data['demand_code'] = PublishService._generate_demand_code()

        # 处理地区信息
        if requirement_data['province'] or requirement_data['city']:
            requirement_data['region'] = {
                'province': requirement_data.pop('province', ''),
                'city': requirement_data.pop('city', '')
            }

        # 创建并保存需求
        requirement = Requirement(**requirement_data)
        success = requirement.save()

        if success:
            print(f"[INFO] 需求创建成功: ID={requirement._id}, 编号={requirement.demand_code}")
            return requirement
        else:
            print(f"[ERROR] 需求保存失败")
            return None

    @staticmethod
    def get_user_achievements(user_id, limit=50, offset=0, exclude_rejected=True, status=None):
        """获取用户提交的成果列表（默认排除已驳回的，可按状态筛选）"""
        achievements = Achievement.find(user_id=user_id)
        # 按创建时间倒序排序
        achievements = sorted(achievements, key=lambda x: x.created_at, reverse=True)
        if status:
            achievements = [a for a in achievements if a.status == status]
        elif exclude_rejected:
            achievements = [a for a in achievements if a.status != 'rejected']
        return achievements[offset:offset+limit] if limit else achievements

    @staticmethod
    def get_user_requirements(user_id, limit=50, offset=0, exclude_rejected=True, status=None):
        """获取用户提交的需求列表（默认排除已驳回的，可按状态筛选）"""
        requirements = Requirement.find(user_id=user_id)
        # 按创建时间倒序排序
        requirements = sorted(requirements, key=lambda x: x.created_at, reverse=True)
        if status:
            requirements = [r for r in requirements if r.status == status]
        elif exclude_rejected:
            requirements = [r for r in requirements if r.status != 'rejected']
        return requirements[offset:offset+limit] if limit else requirements

    @staticmethod
    def get_user_rejected_achievements(user_id, limit=50, offset=0):
        """获取用户被驳回的成果列表"""
        achievements = Achievement.find(user_id=user_id)
        achievements = [a for a in achievements if a.status == 'rejected']
        achievements = sorted(achievements, key=lambda x: x.created_at, reverse=True)
        return achievements[offset:offset+limit] if limit else achievements

    @staticmethod
    def get_user_rejected_requirements(user_id, limit=50, offset=0):
        """获取用户被驳回的需求列表"""
        requirements = Requirement.find(user_id=user_id)
        requirements = [r for r in requirements if r.status == 'rejected']
        requirements = sorted(requirements, key=lambda x: x.created_at, reverse=True)
        return requirements[offset:offset+limit] if limit else requirements

    @staticmethod
    def get_achievement_by_id(achievement_id):
        """根据ID或编号获取成果详情"""
        achievement = Achievement.get(achievement_id)
        if not achievement:
            # 如果按_id没找到，尝试按编号查询
            achievement = Achievement.find_one(achievement_code=achievement_id)
        return achievement

    @staticmethod
    def get_requirement_by_id(requirement_id):
        """根据ID或编号获取需求详情"""
        requirement = Requirement.get(requirement_id)
        if not requirement:
            # 如果按_id没找到，尝试按编号查询
            requirement = Requirement.find_one(demand_code=requirement_id)
        return requirement

    @staticmethod
    def get_pending_achievements(limit=10, offset=0):
        """获取待审核的成果列表（分页）"""
        # 查找状态为'pending'的成果，按创建时间倒序
        achievements = Achievement.find(status='pending')
        # 按创建时间倒序排序
        achievements = sorted(achievements, key=lambda x: x.created_at, reverse=True)
        return achievements[offset:offset+limit] if limit else achievements

    @staticmethod
    def update_achievement_status(achievement_id, status, reviewer_id=None):
        """更新成果状态（审核通过/拒绝）

        Args:
            achievement_id: 成果ID
            status: 新状态 ('approved', 'rejected')
            reviewer_id: 审核人ID（可选）

        Returns:
            更新后的Achievement对象，如果失败返回None
        """
        if status not in ['approved', 'rejected']:
            raise ValueError(f"无效的状态: {status}，有效值: 'approved', 'rejected'")

        achievement = Achievement.get(achievement_id)
        if not achievement:
            return None

        # 更新状态
        achievement.status = status
        # 可以添加审核人信息和审核时间
        if reviewer_id:
            achievement.reviewer_id = reviewer_id
            achievement.reviewed_at = datetime.now()

        success = achievement.save()
        if success:
            print(f"[INFO] 成果状态更新成功: ID={achievement_id}, 新状态={status}")
            return achievement
        else:
            print(f"[ERROR] 成果状态更新失败: ID={achievement_id}")
            return None

    @staticmethod
    def get_pending_requirements(limit=10, offset=0):
        """获取待审核的需求列表（分页）

        Args:
            limit: 每页数量
            offset: 偏移量

        Returns:
            待审核需求列表
        """
        # 查找状态为'pending'的需求，按创建时间倒序
        requirements = Requirement.find(status='pending')
        # 按创建时间倒序排序
        requirements = sorted(requirements, key=lambda x: x.created_at, reverse=True)
        return requirements[offset:offset+limit] if limit else requirements

    @staticmethod
    def update_requirement_status(requirement_id, status, reviewer_id=None):
        """更新需求状态（审核通过/拒绝）

        Args:
            requirement_id: 需求ID
            status: 新状态 ('approved', 'rejected')
            reviewer_id: 审核人ID（可选）

        Returns:
            更新后的Requirement对象，如果失败返回None
        """
        if status not in ['approved', 'rejected']:
            raise ValueError(f"无效的状态: {status}，有效值: 'approved', 'rejected'")

        requirement = Requirement.get(requirement_id)
        if not requirement:
            return None

        # 更新状态
        requirement.status = status
        # 可以添加审核人信息和审核时间
        if reviewer_id:
            requirement.reviewer_id = reviewer_id
            requirement.reviewed_at = datetime.now()

        success = requirement.save()
        if success:
            print(f"[INFO] 需求状态更新成功: ID={requirement_id}, 新状态={status}")
            return requirement
        else:
            print(f"[ERROR] 需求状态更新失败: ID={requirement_id}")
            return None

    @staticmethod
    def update_achievement(achievement_id, form_data):
        """更新已驳回的成果并重新提交审核

        Args:
            achievement_id: 成果ID
            form_data: 前端表单数据（字典）

        Returns:
            更新后的Achievement对象，如果失败返回None
        """
        achievement = Achievement.get(achievement_id)
        if not achievement:
            return None

        # 只允许更新 rejected 状态的成果
        if achievement.status != 'rejected':
            return None

        # 更新字段（与create_achievement相同的映射）
        if 'name' in form_data:
            achievement.achievement_name = form_data['name']
        if 'holder' in form_data:
            achievement.owner = form_data['holder']
        if 'province' in form_data:
            achievement.region['province'] = form_data['province']
        if 'city' in form_data:
            achievement.region['city'] = form_data['city']
        if 'techField' in form_data:
            achievement.tech_fields = [] if form_data['techField'] == '其他' else [form_data['techField']]
        if 'techFieldOther' in form_data:
            achievement.tech_fields_other = form_data['techFieldOther']
        if 'maturity' in form_data:
            achievement.tech_maturity = form_data['maturity']
        if 'transformTypes' in form_data:
            transform_types = form_data['transformTypes']
            if isinstance(transform_types, str):
                transform_types = [item.strip() for item in transform_types.split(',')] if transform_types.strip() else []
            elif not isinstance(transform_types, list):
                transform_types = [transform_types] if transform_types is not None else []
            achievement.transfer_methods = [item for item in transform_types if item != '其他']
        if 'transformOther' in form_data:
            achievement.transfer_methods_other = form_data['transformOther']

        # 更新描述信息
        description = achievement.description or {}
        if 'summary' in form_data:
            description['summary'] = form_data['summary']
        if 'innovationLevel' in form_data:
            description['innovation_level'] = form_data['innovationLevel']
        if 'advantages' in form_data:
            description['advantages'] = form_data['advantages']
        if 'techIndicators' in form_data:
            description['core_indicators'] = form_data['techIndicators']
        if 'intellectualProperty' in form_data:
            description['intellectual_property'] = form_data['intellectualProperty']
        achievement.description = description

        # 更新转化偏好
        if 'cooperationPref' in form_data:
            cooperation_pref = form_data['cooperationPref']
            transfer_preference = achievement.transfer_preference or {}
            transfer_preference['tech_transfer'] = {
                'enabled': cooperation_pref == '技术转让',
                'expected_fee': float(form_data.get('transferFee', 0)) if cooperation_pref == '技术转让' and form_data.get('transferFee') else 0
            }
            transfer_preference['tech_license'] = {
                'enabled': cooperation_pref == '技术许可',
                'type': form_data.get('licenseType', '') if cooperation_pref == '技术许可' else ''
            }
            transfer_preference['tech_investment'] = {
                'enabled': cooperation_pref == '技术入股',
                'valuation': float(form_data.get('equityValue', 0)) if cooperation_pref == '技术入股' and form_data.get('equityValue') else 0,
                'share_ratio': float(form_data.get('equityPercent', 0)) if cooperation_pref == '技术入股' and form_data.get('equityPercent') else 0
            }
            transfer_preference['cooperation_dev'] = cooperation_pref == '合作开发'
            transfer_preference['other'] = form_data.get('cooperationOther', '') if cooperation_pref == '其他' else ''
            transfer_preference['preferred_method'] = cooperation_pref
            achievement.transfer_preference = transfer_preference

        # 重置状态为待审核
        achievement.status = 'pending'
        # 清除驳回原因
        achievement.reject_reason = ''
        # 清除审核信息
        achievement.reviewer_id = None
        achievement.reviewed_at = None

        success = achievement.save()
        if success:
            print(f"[INFO] 成果更新并重新提交成功: ID={achievement_id}")
            return achievement
        else:
            print(f"[ERROR] 成果更新失败: ID={achievement_id}")
            return None

    @staticmethod
    def update_requirement(requirement_id, form_data):
        """更新已驳回的需求并重新提交审核

        Args:
            requirement_id: 需求ID
            form_data: 前端表单数据（字典）

        Returns:
            更新后的Requirement对象，如果失败返回None
        """
        requirement = Requirement.get(requirement_id)
        if not requirement:
            return None

        # 只允许更新 rejected 状态的需求
        if requirement.status != 'rejected':
            return None

        # 更新字段（与create_requirement相同的映射）
        if 'companyName' in form_data:
            requirement.company_name = form_data['companyName']
        if 'demandName' in form_data:
            requirement.demand_name = form_data['demandName']
        if 'province' in form_data:
            requirement.region['province'] = form_data['province']
        if 'city' in form_data:
            requirement.region['city'] = form_data['city']
        if 'techField' in form_data:
            requirement.tech_fields = [] if form_data['techField'] == '其他' else [form_data['techField']]
        if 'techFieldOther' in form_data:
            requirement.tech_fields_other = form_data['techFieldOther']
        if 'demandType' in form_data:
            requirement.demand_types = [] if form_data['demandType'] == '其他' else [form_data['demandType']]
        if 'demandTypeOther' in form_data:
            requirement.demand_types_other = form_data['demandTypeOther']
        if 'description' in form_data:
            requirement.description['overview'] = form_data['description']
        if 'expectedProblem' in form_data:
            requirement.description['target_problems'] = form_data['expectedProblem']

        # 更新预算
        if 'budget' in form_data:
            budget = form_data['budget']
            if budget:
                try:
                    budget_value = float(budget)
                    budget_unit = form_data.get('budgetUnit', '万元')
                    if budget_unit == '元':
                        budget_value = budget_value / 10000
                    elif budget_unit == '百万元':
                        budget_value = budget_value * 100
                    elif budget_unit == '亿元':
                        budget_value = budget_value * 10000
                    requirement.description['budget'] = budget_value
                except (ValueError, TypeError):
                    pass

        # 重置状态为待审核
        requirement.status = 'pending'
        # 清除驳回原因
        requirement.reject_reason = ''
        # 清除审核信息
        requirement.reviewer_id = None
        requirement.reviewed_at = None

        success = requirement.save()
        if success:
            print(f"[INFO] 需求更新并重新提交成功: ID={requirement_id}")
            return requirement
        else:
            print(f"[ERROR] 需求更新失败: ID={requirement_id}")
            return None


    @staticmethod
    def toggle_achievement_display(achievement_id, is_display):
        """
        切换成果的主页展示状态 (is_display)

        Args:
            achievement_id: 成果ID
            is_display: 布尔值 (True 展示 / False 隐藏)

        Returns:
            更新后的Achievement对象，如果失败返回None
        """
        achievement = Achievement.get(achievement_id)
        if not achievement:
            return None

        # 更新展示状态
        achievement.is_display = bool(is_display)

        success = achievement.save()
        if success:
            print(f"[INFO] 成果展示状态更新成功: ID={achievement_id}, is_display={is_display}")
            return achievement
        else:
            print(f"[ERROR] 成果展示状态更新失败: ID={achievement_id}")
            return None


    @staticmethod
    def toggle_requirement_display(requirement_id, is_display):
        """
        切换需求的主页展示状态 (is_display)

        Args:
            requirement_id: 需求ID
            is_display: 布尔值 (True 展示 / False 隐藏)

        Returns:
            更新后的Requirement对象，如果失败返回None
        """
        requirement = Requirement.get(requirement_id)
        if not requirement:
            return None

        # 更新展示状态
        requirement.is_display = bool(is_display)

        success = requirement.save()
        if success:
            print(f"[INFO] 需求展示状态更新成功: ID={requirement_id}, is_display={is_display}")
            return requirement
        else:
            print(f"[ERROR] 需求展示状态更新失败: ID={requirement_id}")
            return None

    @staticmethod
    def get_public_achievements(limit=6):
        """获取主页展示的成果（已审核且允许展示）"""
        # 利用你封装的 find 方法，直接传入多个匹配条件
        achievements = Achievement.find(status='approved', is_display=True)
        # 按创建时间倒序排序，最新的展示在前面
        achievements = sorted(achievements, key=PublishService._safe_sort_key, reverse=True)
        return achievements[:limit] if limit else achievements

    @staticmethod
    def get_public_requirements(limit=6):
        """获取主页展示的需求（已审核且允许展示）"""
        requirements = Requirement.find(status='approved', is_display=True)
        requirements = sorted(requirements, key=PublishService._safe_sort_key, reverse=True)
        return requirements[:limit] if limit else requirements

    @staticmethod
    def get_all_approved_achievements(limit=50, offset=0):
        """获取所有已审核通过的成果（用于成果中心）"""
        achievements = Achievement.find(status='approved')
        # 按创建时间倒序排序
        achievements = sorted(achievements, key=PublishService._safe_sort_key, reverse=True)
        return achievements[offset:offset+limit] if limit else achievements

    @staticmethod
    def get_all_approved_requirements(limit=50, offset=0):
        """获取所有已审核通过的需求（用于需求中心）"""
        requirements = Requirement.find(status='approved')
        requirements = sorted(requirements, key=PublishService._safe_sort_key, reverse=True)
        return requirements[offset:offset+limit] if limit else requirements

    @staticmethod
    def get_all_achievements(limit=50, offset=0):
        """获取所有成果（不限状态，用于管理员管理）"""
        achievements = Achievement.find()
        # 先按创建时间倒序
        achievements = sorted(achievements, key=PublishService._safe_sort_key, reverse=True)
        # 再稳定排序：已展示的置顶
        achievements.sort(key=lambda x: not getattr(x, 'is_display', False))
        return achievements[offset:offset+limit] if limit else achievements

    @staticmethod
    def get_all_requirements(limit=50, offset=0):
        """获取所有需求（不限状态，用于管理员管理）"""
        requirements = Requirement.find()
        # 先按创建时间倒序
        requirements = sorted(requirements, key=PublishService._safe_sort_key, reverse=True)
        # 再稳定排序：已展示的置顶
        requirements.sort(key=lambda x: not getattr(x, 'is_display', False))
        return requirements[offset:offset+limit] if limit else requirements

    @staticmethod
    def delete_achievement(achievement_id):
        """删除成果"""
        achievement = Achievement.get(achievement_id)
        if not achievement:
            return False
        success = achievement.delete()
        if success:
            print(f"[INFO] 成果删除成功: ID={achievement_id}")
        else:
            print(f"[ERROR] 成果删除失败: ID={achievement_id}")
        return success

    @staticmethod
    def delete_requirement(requirement_id):
        """删除需求"""
        requirement = Requirement.get(requirement_id)
        if not requirement:
            return False
        success = requirement.delete()
        if success:
            print(f"[INFO] 需求删除成功: ID={requirement_id}")
        else:
            print(f"[ERROR] 需求删除失败: ID={requirement_id}")
        return success

    @staticmethod
    def admin_update_achievement(achievement_id, data):
        """管理员更新成果信息（无状态限制）"""
        achievement = Achievement.get(achievement_id)
        if not achievement:
            return None

        if 'achievement_name' in data:
            achievement.achievement_name = data['achievement_name']
        if 'owner' in data:
            achievement.owner = data['owner']
        if 'tech_fields' in data:
            achievement.tech_fields = data['tech_fields'] if isinstance(data['tech_fields'], list) else []
        if 'tech_fields_other' in data:
            achievement.tech_fields_other = data['tech_fields_other']
        if 'tech_maturity' in data:
            achievement.tech_maturity = data['tech_maturity']
        if 'transfer_methods' in data:
            achievement.transfer_methods = data['transfer_methods'] if isinstance(data['transfer_methods'], list) else []
        if 'transfer_methods_other' in data:
            achievement.transfer_methods_other = data['transfer_methods_other']
        if 'region' in data:
            region = data['region']
            if isinstance(region, dict):
                achievement.region = region

        # 更新描述信息
        description = achievement.description or {}
        desc_data = data.get('description', {})
        if isinstance(desc_data, dict):
            for key in ['summary', 'innovation_level', 'advantages', 'core_indicators', 'intellectual_property']:
                if key in desc_data:
                    description[key] = desc_data[key]
            achievement.description = description

        # 更新转化偏好
        if 'transfer_preference' in data:
            tp = achievement.transfer_preference or {}
            tp_data = data['transfer_preference']
            if isinstance(tp_data, dict):
                for key in tp_data:
                    tp[key] = tp_data[key]
                achievement.transfer_preference = tp

        success = achievement.save()
        if success:
            print(f"[INFO] 管理员更新成果成功: ID={achievement_id}")
            return achievement
        else:
            print(f"[ERROR] 管理员更新成果失败: ID={achievement_id}")
            return None

    @staticmethod
    def admin_update_requirement(requirement_id, data):
        """管理员更新需求信息（无状态限制）"""
        requirement = Requirement.get(requirement_id)
        if not requirement:
            return None

        if 'demand_name' in data:
            requirement.demand_name = data['demand_name']
        if 'company_name' in data:
            requirement.company_name = data['company_name']
        if 'tech_fields' in data:
            requirement.tech_fields = data['tech_fields'] if isinstance(data['tech_fields'], list) else []
        if 'tech_fields_other' in data:
            requirement.tech_fields_other = data['tech_fields_other']
        if 'demand_types' in data:
            requirement.demand_types = data['demand_types'] if isinstance(data['demand_types'], list) else []
        if 'demand_types_other' in data:
            requirement.demand_types_other = data['demand_types_other']
        if 'match_status' in data:
            match_status = data['match_status']
            if match_status in ('待对接', '对接中', '已完成'):
                requirement.match_status = match_status
        if 'region' in data:
            region = data['region']
            if isinstance(region, dict):
                requirement.region = region

        # 更新描述信息
        description = requirement.description or {}
        desc_data = data.get('description', {})
        if isinstance(desc_data, dict):
            for key in ['overview', 'target_problems', 'budget']:
                if key in desc_data:
                    description[key] = desc_data[key]
            requirement.description = description

        success = requirement.save()
        if success:
            print(f"[INFO] 管理员更新需求成功: ID={requirement_id}")
            return requirement
        else:
            print(f"[ERROR] 管理员更新需求失败: ID={requirement_id}")
            return None

    # ========== 专家管理 ==========

    @staticmethod
    def create_expert(data):
        """创建专家记录"""
        expert = Expert(**data)
        success = expert.save()
        if success:
            print(f"[INFO] 专家创建成功: ID={expert._id}, 姓名={expert.name}")
            return expert
        else:
            print(f"[ERROR] 专家保存失败")
            return None

    @staticmethod
    def get_experts(limit=10, offset=0):
        """获取专家列表（分页）"""
        experts = Expert.find()
        experts = sorted(experts, key=lambda x: x.created_at, reverse=True)
        return experts[offset:offset+limit] if limit else experts

    @staticmethod
    def get_expert_by_id(expert_id):
        """根据ID获取专家详情"""
        return Expert.get(expert_id)

    @staticmethod
    def update_expert(expert_id, data):
        """更新专家信息"""
        expert = Expert.get(expert_id)
        if not expert:
            return None

        for key, value in data.items():
            if hasattr(expert, key):
                setattr(expert, key, value)

        success = expert.save()
        if success:
            print(f"[INFO] 专家更新成功: ID={expert_id}")
            return expert
        else:
            print(f"[ERROR] 专家更新失败: ID={expert_id}")
            return None

    @staticmethod
    def delete_expert(expert_id):
        """删除专家记录（同时清理附件文件）"""
        expert = Expert.get(expert_id)
        if not expert:
            return False

        # 删除专家照片文件夹
        expert_name = expert.name
        if expert_name:
            experts_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'experts_images')
            expert_folder = os.path.join(experts_images_dir, expert_name)
            if os.path.exists(expert_folder):
                try:
                    shutil.rmtree(expert_folder)
                    print(f"[INFO] 专家附件文件夹已删除: {expert_folder}")
                except Exception as e:
                    print(f"[ERROR] 删除专家附件文件夹失败: {e}")

        success = expert.delete()
        if success:
            print(f"[INFO] 专家删除成功: ID={expert_id}")
        else:
            print(f"[ERROR] 专家删除失败: ID={expert_id}")
        return success

    @staticmethod
    def add_expert_attachment(expert_id, attachment_type, file_info):
        """向专家文档添加附件记录"""
        expert = Expert.get(expert_id)
        if not expert:
            return False

        # attachments 结构: {"身份证件复印件": [{"file_name":..., "file_path":..., "file_url":...}, ...]}
        if not hasattr(expert, 'attachments') or not expert.attachments:
            expert.attachments = {}

        if attachment_type not in expert.attachments:
            expert.attachments[attachment_type] = []

        expert.attachments[attachment_type].append(file_info)
        return expert.save()

    @staticmethod
    def remove_expert_attachment(expert_id, attachment_type, file_name):
        """从专家文档移除附件记录"""
        expert = Expert.get(expert_id)
        if not expert:
            return False

        if hasattr(expert, 'attachments') and expert.attachments:
            if attachment_type in expert.attachments:
                expert.attachments[attachment_type] = [
                    f for f in expert.attachments[attachment_type]
                    if f.get('file_name') != file_name
                ]
        return expert.save()

    # ========== 合作伙伴管理 ==========

    @staticmethod
    def create_partner(data):
        """创建合作伙伴记录"""
        partner = Partner(**data)
        success = partner.save()
        if success:
            print(f"[INFO] 合作伙伴创建成功: ID={partner._id}, 名称={partner.name}")
            return partner
        else:
            print(f"[ERROR] 合作伙伴保存失败")
            return None

    @staticmethod
    def get_partners(limit=10, offset=0, type_filter=None):
        """获取合作伙伴列表（分页），可按类型筛选"""
        if type_filter:
            partners = Partner.find(type=type_filter)
        else:
            partners = Partner.find()
        partners = sorted(partners, key=lambda x: x.created_at, reverse=True)
        return partners[offset:offset+limit] if limit else partners

    @staticmethod
    def get_partner_by_id(partner_id):
        """根据ID获取合作伙伴详情"""
        return Partner.get(partner_id)

    @staticmethod
    def update_partner(partner_id, data):
        """更新合作伙伴信息"""
        partner = Partner.get(partner_id)
        if not partner:
            return None

        for key, value in data.items():
            if hasattr(partner, key):
                setattr(partner, key, value)

        success = partner.save()
        if success:
            print(f"[INFO] 合作伙伴更新成功: ID={partner_id}")
            return partner
        else:
            print(f"[ERROR] 合作伙伴更新失败: ID={partner_id}")
            return None

    @staticmethod
    def delete_partner(partner_id):
        """删除合作伙伴记录（同时清理图片文件夹）"""
        partner = Partner.get(partner_id)
        if not partner:
            return False

        # 删除合作伙伴图片文件夹
        partner_name = partner.name
        if partner_name:
            partners_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'partners_images')
            partner_folder = os.path.join(partners_images_dir, partner_name)
            if os.path.exists(partner_folder):
                try:
                    shutil.rmtree(partner_folder)
                    print(f"[INFO] 合作伙伴图片文件夹已删除: {partner_folder}")
                except Exception as e:
                    print(f"[ERROR] 删除合作伙伴图片文件夹失败: {e}")

        success = partner.delete()
        if success:
            print(f"[INFO] 合作伙伴删除成功: ID={partner_id}")
        else:
            print(f"[ERROR] 合作伙伴删除失败: ID={partner_id}")
        return success

    @staticmethod
    def add_partner_image(partner_id, file_info):
        """向合作伙伴添加图片记录"""
        partner = Partner.get(partner_id)
        if not partner:
            return False

        if not hasattr(partner, 'images') or not partner.images:
            partner.images = []

        partner.images.append(file_info)
        return partner.save()

    @staticmethod
    def remove_partner_image(partner_id, file_name):
        """从合作伙伴移除图片记录"""
        partner = Partner.get(partner_id)
        if not partner:
            return False

        if hasattr(partner, 'images') and partner.images:
            partner.images = [f for f in partner.images if f.get('file_name') != file_name]
        return partner.save()

    # ========== 金融服务管理 ==========

    @staticmethod
    def create_financial_service(data):
        """创建金融服务机构记录"""
        from .mongo_models import FinancialService
        fs = FinancialService(**data)
        success = fs.save()
        if success:
            print(f"[INFO] 金融服务机构创建成功: ID={fs._id}, 名称={fs.name}")
            return fs
        else:
            print(f"[ERROR] 金融服务机构保存失败")
            return None

    @staticmethod
    def get_financial_services(limit=10, offset=0):
        """获取金融服务机构列表（分页）"""
        from .mongo_models import FinancialService
        fss = FinancialService.find()
        fss = sorted(fss, key=lambda x: x.created_at, reverse=True)
        return fss[offset:offset+limit] if limit else fss

    @staticmethod
    def get_financial_service_by_id(fs_id):
        """根据ID获取金融服务机构详情"""
        from .mongo_models import FinancialService
        return FinancialService.get(fs_id)

    @staticmethod
    def update_financial_service(fs_id, data):
        """更新金融服务机构信息"""
        from .mongo_models import FinancialService
        fs = FinancialService.get(fs_id)
        if not fs:
            return None

        for key, value in data.items():
            if hasattr(fs, key):
                setattr(fs, key, value)

        success = fs.save()
        if success:
            print(f"[INFO] 金融服务机构更新成功: ID={fs_id}")
            return fs
        else:
            print(f"[ERROR] 金融服务机构更新失败: ID={fs_id}")
            return None

    @staticmethod
    def delete_financial_service(fs_id):
        """删除金融服务机构记录（同时清理图片文件夹）"""
        from .mongo_models import FinancialService
        fs = FinancialService.get(fs_id)
        if not fs:
            return False

        # 删除图片文件夹
        fs_name = fs.name
        if fs_name:
            fin_images_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'financial_services_images')
            fs_folder = os.path.join(fin_images_dir, fs_name)
            if os.path.exists(fs_folder):
                try:
                    shutil.rmtree(fs_folder)
                    print(f"[INFO] 金融服务机构图片文件夹已删除: {fs_folder}")
                except Exception as e:
                    print(f"[ERROR] 删除金融服务机构图片文件夹失败: {e}")

        success = fs.delete()
        if success:
            print(f"[INFO] 金融服务机构删除成功: ID={fs_id}")
        else:
            print(f"[ERROR] 金融服务机构删除失败: ID={fs_id}")
        return success

    @staticmethod
    def add_financial_service_image(fs_id, file_info):
        """向金融服务机构添加图片记录"""
        from .mongo_models import FinancialService
        fs = FinancialService.get(fs_id)
        if not fs:
            return False

        if not hasattr(fs, 'images') or not fs.images:
            fs.images = []

        fs.images.append(file_info)
        return fs.save()

    @staticmethod
    def remove_financial_service_image(fs_id, file_name):
        """从金融服务机构移除图片记录"""
        from .mongo_models import FinancialService
        fs = FinancialService.get(fs_id)
        if not fs:
            return False

        if hasattr(fs, 'images') and fs.images:
            fs.images = [f for f in fs.images if f.get('file_name') != file_name]
        return fs.save()


# ========== 合作申请管理 ==========

class CooperationService:

    @staticmethod
    def create_cooperation(data):
        """创建合作申请"""
        cooperation = Cooperation(**data)
        success = cooperation.save()
        if success:
            print(f"[INFO] 合作申请创建成功: ID={cooperation._id}")
            return cooperation
        else:
            print(f"[ERROR] 合作申请保存失败")
            return None

    @staticmethod
    def get_cooperations(limit=50, offset=0):
        """获取合作申请列表（按时间倒序）"""
        cooperations = Cooperation.find()
        cooperations = sorted(cooperations, key=lambda x: x.created_at, reverse=True)
        return cooperations[offset:offset+limit] if limit else cooperations

    @staticmethod
    def get_cooperation_by_id(cooperation_id):
        """根据ID获取合作申请"""
        return Cooperation.get(cooperation_id)

    @staticmethod
    def delete_cooperation(cooperation_id):
        """删除合作申请"""
        cooperation = Cooperation.get(cooperation_id)
        if not cooperation:
            return False
        success = cooperation.delete()
        if success:
            print(f"[INFO] 合作申请删除成功: ID={cooperation_id}")
        else:
            print(f"[ERROR] 合作申请删除失败: ID={cooperation_id}")
        return success