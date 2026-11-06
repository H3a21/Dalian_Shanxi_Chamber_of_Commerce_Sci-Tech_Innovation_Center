<template>
  <div class="require-page">
    <div v-if="dataLoading" class="form-loading">加载中...</div>
    <div class="require-container" v-show="!dataLoading">
      <div class="top-bar" v-if="!isDialog">
        <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="form-title">《需求采集表》</h1>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="left" label-width="160px" class="require-form">
        <div class="section-title">一、需求基本信息</div>
        <table class="form-table">
          <tbody>
          <tr>
            <th><span class="required">*</span> 企业名称</th>
            <td>
              <el-form-item prop="companyName" class="table-form-item">
                <el-input v-model="form.companyName" placeholder="请输入企业全称" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 需求名称</th>
            <td>
              <el-form-item prop="demandName" class="table-form-item">
                <el-input v-model="form.demandName" placeholder="请输入需求名称" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 所属地区</th>
            <td>
              <el-form-item prop="region" class="table-form-item">
                <div class="region-selectors">
                  <el-select v-model="form.province" placeholder="选择省份">
                    <el-option v-for="province in provinces" :key="province" :label="province" :value="province" />
                  </el-select>
                  <el-select v-model="form.city" :placeholder="isMunicipality ? '选择区' : '选择城市'" :disabled="!form.province">
                    <el-option v-for="city in cities" :key="city" :label="city" :value="city" />
                  </el-select>
                </div>
                <div v-if="form.region" style="margin-top: 8px; color: #666; font-size: 14px;">
                  已选择：{{ form.region }}
                </div>
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 应用领域</th>
            <td>
              <el-form-item prop="techField" class="table-form-item">
                <div class="industry-group">
                  <div class="industry-category">
                    <div class="category-title">战略性新兴产业（最多选一个）</div>
                    <el-radio-group v-model="form.emergingIndustry">
                      <el-radio value="节能环保产业">节能环保产业</el-radio>
                      <el-radio value="新一代信息技术产业">新一代信息技术产业</el-radio>
                      <el-radio value="高端装备制造产业">高端装备制造产业</el-radio>
                      <el-radio value="新能源产业">新能源产业</el-radio>
                      <el-radio value="新材料产业">新材料产业</el-radio>
                      <el-radio value="生物产业">生物产业</el-radio>
                      <el-radio value="新能源汽车产业">新能源汽车产业</el-radio>
                      <el-radio value="数字创意产业">数字创意产业</el-radio>
                    </el-radio-group>
                  </div>
                  <div class="industry-category">
                    <div class="category-title">传统产业（最多选一个）</div>
                    <el-radio-group v-model="form.traditionalIndustry">
                      <el-radio value="农、林、牧、渔业">农、林、牧、渔业</el-radio>
                      <el-radio value="采矿业">采矿业</el-radio>
                      <el-radio value="制造业">制造业</el-radio>
                      <el-radio value="水利环境">水利环境</el-radio>
                      <el-radio value="教育，医疗卫生">教育，医疗卫生</el-radio>
                      <el-radio value="文化、体育和娱乐">文化、体育和娱乐</el-radio>
                      <el-radio value="电力、热力和燃气">电力、热力和燃气</el-radio>
                      <el-radio value="建筑业">建筑业</el-radio>
                      <el-radio value="交通运输和仓储">交通运输和仓储</el-radio>
                      <el-radio value="住宿和餐饮业">住宿和餐饮业</el-radio>
                      <el-radio value="信息传输、软件和信息技术服务业">信息传输、软件和信息技术服务业</el-radio>
                      <el-radio value="金融业">金融业</el-radio>
                      <el-radio value="房地产业">房地产业</el-radio>
                      <el-radio value="新能源">新能源</el-radio>
                      <el-radio value="科学研究和技术服务">科学研究和技术服务</el-radio>
                    </el-radio-group>
                  </div>
                </div>
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 需求类型</th>
            <td>
              <el-form-item prop="demandType" class="table-form-item">
                <el-select v-model="form.demandType" placeholder="--请选择--">
                  <el-option label="技术需求" value="技术需求" />
                  <el-option label="金融需求" value="金融需求" />
                  <el-option label="场景需求" value="场景需求" />
                  <el-option label="其他" value="其他" />
                </el-select>
              </el-form-item>
              <el-form-item v-if="form.demandType === '其他'" prop="demandTypeOther" class="table-form-item" style="margin-top: 8px;">
                <el-input v-model="form.demandTypeOther" placeholder="请填写具体需求类型" />
              </el-form-item>
            </td>
          </tr>
          </tbody>
        </table>

        <div class="section-title">二、需求描述</div>
        <table class="form-table">
          <tbody>
          <tr>
            <th><span class="required">*</span> 需求概述</th>
            <td>
              <el-form-item prop="description" class="table-form-item">
                <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请详细描述需求的主要内容" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 期望解决的问题</th>
            <td>
              <el-form-item prop="expectedProblem" class="table-form-item">
                <el-input v-model="form.expectedProblem" type="textarea" :rows="4" placeholder="请描述期望通过该需求解决的具体问题" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th>项目预算</th>
            <td>
              <div style="display: flex; align-items: center; gap: 10px;">
                <el-input-number v-model="form.budget" :precision="2" :controls="false" placeholder="请输入金额" style="width: 200px;" />
                <el-select v-model="form.budgetUnit" style="width: 120px;">
                  <el-option v-for="option in budgetUnitOptions" :key="option.value" :label="option.label" :value="option.value" />
                </el-select>
              </div>
            </td>
          </tr>
          </tbody>
        </table>
      </el-form>

      <div class="notes-section">
        <div class="notes-title">注：</div>
        <ol class="notes-list">
          <li>请确保所填信息的真实性与合法性；</li>
          <li>提交成功后，系统将进入"管理员审核"流程，周期一般为 1-3 个工作日；</li>
          <li>审核结果将通过站内信或短信通知，审核通过后自动在"需求中心"展示。</li>
        </ol>
      </div>

      <div class="bottom-actions" v-if="!isDialog">
        <el-button @click="goBack" size="large">返回</el-button>
        <el-button type="primary" @click="submitForm" size="large" :loading="loading">提交审核</el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import request from '../utils/request'

export default {
  name: 'RequireView',
  props: {
    isDialog: {
      type: Boolean,
      default: false
    },
    editId: {
      type: [String, Number],
      default: null
    },
    isAdminEdit: {
      type: Boolean,
      default: false
    }
  },
  setup(props, { emit }) {
    const router = useRouter()
    const formRef = ref(null)
    const loading = ref(false)
    const dataLoading = ref(false)
    const isPopulating = ref(false)

    const emergingIndustries = [
      '节能环保产业', '新一代信息技术产业', '高端装备制造产业', '新能源产业',
      '新材料产业', '生物产业', '新能源汽车产业', '数字创意产业'
    ]
    const traditionalIndustries = [
      '农、林、牧、渔业', '采矿业', '制造业', '水利环境', '教育，医疗卫生',
      '文化、体育和娱乐', '电力、热力和燃气', '建筑业', '交通运输和仓储',
      '住宿和餐饮业', '信息传输、软件和信息技术服务业', '金融业', '房地产业',
      '新能源', '科学研究和技术服务'
    ]
    const demandTypeOptions = ['技术需求', '金融需求', '场景需求', '其他']

    // 省份数据（包括直辖市、特别行政区、台湾）
    const provinces = [
      '北京市', '天津市', '上海市', '重庆市',
      '河北省', '山西省', '辽宁省', '吉林省', '黑龙江省',
      '江苏省', '浙江省', '安徽省', '福建省', '江西省', '山东省',
      '河南省', '湖北省', '湖南省', '广东省', '海南省',
      '四川省', '贵州省', '云南省', '陕西省', '甘肃省',
      '青海省', '台湾省',
      '内蒙古自治区', '广西壮族自治区', '西藏自治区', '宁夏回族自治区', '新疆维吾尔自治区',
      '香港特别行政区', '澳门特别行政区'
    ]

    // 城市映射（直辖市显示区）
    const citiesMap = {
      '北京市': ['东城区', '西城区', '朝阳区', '丰台区', '石景山区', '海淀区', '门头沟区', '房山区', '通州区', '顺义区', '昌平区', '大兴区', '怀柔区', '平谷区', '密云区', '延庆区'],
      '天津市': ['和平区', '河东区', '河西区', '南开区', '河北区', '红桥区', '东丽区', '西青区', '津南区', '北辰区', '武清区', '宝坻区', '滨海新区', '宁河区', '静海区', '蓟州区'],
      '上海市': ['黄浦区', '徐汇区', '长宁区', '静安区', '普陀区', '虹口区', '杨浦区', '闵行区', '宝山区', '嘉定区', '浦东新区', '金山区', '松江区', '青浦区', '奉贤区', '崇明区'],
      '重庆市': ['万州区', '涪陵区', '渝中区', '大渡口区', '江北区', '沙坪坝区', '九龙坡区', '南岸区', '北碚区', '綦江区', '大足区', '渝北区', '巴南区', '黔江区', '长寿区', '江津区', '合川区', '永川区', '南川区', '璧山区', '铜梁区', '潼南区', '荣昌区', '开州区', '梁平区', '武隆区', '城口县', '丰都县', '垫江县', '忠县', '云阳县', '奉节县', '巫山县', '巫溪县', '石柱土家族自治县', '秀山土家族苗族自治县', '酉阳土家族苗族自治县', '彭水苗族土家族自治县'],
      '河北省': ['石家庄市', '唐山市', '秦皇岛市', '邯郸市', '邢台市', '保定市', '张家口市', '承德市', '沧州市', '廊坊市', '衡水市'],
      '山西省': ['太原市', '大同市', '阳泉市', '长治市', '晋城市', '朔州市', '晋中市', '运城市', '忻州市', '临汾市', '吕梁市'],
      '辽宁省': ['沈阳市', '大连市', '鞍山市', '抚顺市', '本溪市', '丹东市', '锦州市', '营口市', '阜新市', '辽阳市', '盘锦市', '铁岭市', '朝阳市', '葫芦岛市'],
      '吉林省': ['长春市', '吉林市', '四平市', '辽源市', '通化市', '白山市', '松原市', '白城市', '延边朝鲜族自治州'],
      '黑龙江省': ['哈尔滨市', '齐齐哈尔市', '鸡西市', '鹤岗市', '双鸭山市', '大庆市', '伊春市', '佳木斯市', '七台河市', '牡丹江市', '黑河市', '绥化市', '大兴安岭地区'],
      '江苏省': ['南京市', '无锡市', '徐州市', '常州市', '苏州市', '南通市', '连云港市', '淮安市', '盐城市', '扬州市', '镇江市', '泰州市', '宿迁市'],
      '浙江省': ['杭州市', '宁波市', '温州市', '嘉兴市', '湖州市', '绍兴市', '金华市', '衢州市', '舟山市', '台州市', '丽水市'],
      '安徽省': ['合肥市', '芜湖市', '蚌埠市', '淮南市', '马鞍山市', '淮北市', '铜陵市', '安庆市', '黄山市', '滁州市', '阜阳市', '宿州市', '六安市', '亳州市', '池州市', '宣城市'],
      '福建省': ['福州市', '厦门市', '莆田市', '三明市', '泉州市', '漳州市', '南平市', '龙岩市', '宁德市'],
      '江西省': ['南昌市', '景德镇市', '萍乡市', '九江市', '新余市', '鹰潭市', '赣州市', '吉安市', '宜春市', '抚州市', '上饶市'],
      '山东省': ['济南市', '青岛市', '淄博市', '枣庄市', '东营市', '烟台市', '潍坊市', '济宁市', '泰安市', '威海市', '日照市', '临沂市', '德州市', '聊城市', '滨州市', '菏泽市'],
      '河南省': ['郑州市', '开封市', '洛阳市', '平顶山市', '安阳市', '鹤壁市', '新乡市', '焦作市', '濮阳市', '许昌市', '漯河市', '三门峡市', '南阳市', '商丘市', '信阳市', '周口市', '驻马店市'],
      '湖北省': ['武汉市', '黄石市', '十堰市', '宜昌市', '襄阳市', '鄂州市', '荆门市', '孝感市', '荆州市', '黄冈市', '咸宁市', '随州市', '恩施土家族苗族自治州'],
      '湖南省': ['长沙市', '株洲市', '湘潭市', '衡阳市', '邵阳市', '岳阳市', '常德市', '张家界市', '益阳市', '郴州市', '永州市', '怀化市', '娄底市', '湘西土家族苗族自治州'],
      '广东省': ['广州市', '韶关市', '深圳市', '珠海市', '汕头市', '佛山市', '江门市', '湛江市', '茂名市', '肇庆市', '惠州市', '梅州市', '汕尾市', '河源市', '阳江市', '清远市', '东莞市', '中山市', '潮州市', '揭阳市', '云浮市'],
      '海南省': ['海口市', '三亚市', '三沙市', '儋州市'],
      '四川省': ['成都市', '自贡市', '攀枝花市', '泸州市', '德阳市', '绵阳市', '广元市', '遂宁市', '内江市', '乐山市', '南充市', '眉山市', '宜宾市', '广安市', '达州市', '雅安市', '巴中市', '资阳市', '阿坝藏族羌族自治州', '甘孜藏族自治州', '凉山彝族自治州'],
      '贵州省': ['贵阳市', '六盘水市', '遵义市', '安顺市', '毕节市', '铜仁市', '黔西南布依族苗族自治州', '黔东南苗族侗族自治州', '黔南布依族苗族自治州'],
      '云南省': ['昆明市', '曲靖市', '玉溪市', '保山市', '昭通市', '丽江市', '普洱市', '临沧市', '楚雄彝族自治州', '红河哈尼族彝族自治州', '文山壮族苗族自治州', '西双版纳傣族自治州', '大理白族自治州', '德宏傣族景颇族自治州', '怒江傈僳族自治州', '迪庆藏族自治州'],
      '陕西省': ['西安市', '铜川市', '宝鸡市', '咸阳市', '渭南市', '延安市', '汉中市', '榆林市', '安康市', '商洛市'],
      '甘肃省': ['兰州市', '嘉峪关市', '金昌市', '白银市', '天水市', '武威市', '张掖市', '平凉市', '酒泉市', '庆阳市', '定西市', '陇南市', '临夏回族自治州', '甘南藏族自治州'],
      '青海省': ['西宁市', '海东市', '海北藏族自治州', '黄南藏族自治州', '海南藏族自治州', '果洛藏族自治州', '玉树藏族自治州', '海西蒙古族藏族自治州'],
      '台湾省': ['台北市', '高雄市', '基隆市', '台中市', '台南市', '新竹市', '嘉义市', '新北市', '宜兰县', '桃园市', '苗栗县', '彰化县', '南投县', '云林县', '屏东县', '台东县', '花莲县', '澎湖县', '金门县', '连江县'],
      '内蒙古自治区': ['呼和浩特市', '包头市', '乌海市', '赤峰市', '通辽市', '鄂尔多斯市', '呼伦贝尔市', '巴彦淖尔市', '乌兰察布市', '兴安盟', '锡林郭勒盟', '阿拉善盟'],
      '广西壮族自治区': ['南宁市', '柳州市', '桂林市', '梧州市', '北海市', '防城港市', '钦州市', '贵港市', '玉林市', '百色市', '贺州市', '河池市', '来宾市', '崇左市'],
      '西藏自治区': ['拉萨市', '日喀则市', '昌都市', '林芝市', '山南市', '那曲市', '阿里地区'],
      '宁夏回族自治区': ['银川市', '石嘴山市', '吴忠市', '固原市', '中卫市'],
      '新疆维吾尔自治区': ['乌鲁木齐市', '克拉玛依市', '吐鲁番市', '哈密市', '昌吉回族自治州', '博尔塔拉蒙古自治州', '巴音郭楞蒙古自治州', '阿克苏地区', '克孜勒苏柯尔克孜自治州', '喀什地区', '和田地区', '伊犁哈萨克自治州', '塔城地区', '阿勒泰地区'],
      '香港特别行政区': ['香港岛', '九龙', '新界'],
      '澳门特别行政区': ['澳门半岛', '氹仔岛', '路环岛']
    }

    const form = reactive({
      companyName: '',
      demandName: '',
      region: '',
      province: '',
      city: '',
      emergingIndustry: '',
      traditionalIndustry: '',
      demandType: '',
      demandTypeOther: '',
      description: '',
      expectedProblem: '',
      budget: null,
      budgetUnit: '万元'
    })

    const cities = computed(() => {
      if (form.province && citiesMap[form.province]) {
        return citiesMap[form.province]
      }
      return []
    })

    const isMunicipality = computed(() => {
      return form.province && ['北京市', '天津市', '上海市', '重庆市'].includes(form.province)
    })

    watch(() => form.province, (newProvince) => {
      if (isPopulating.value) return
      form.city = ''
      form.region = newProvince
    })

    watch(() => form.city, (newCity) => {
      if (form.province && newCity) {
        form.region = form.province + ' ' + newCity
      } else if (form.province) {
        form.region = form.province
      } else {
        form.region = ''
      }
    })

    const rules = {
      companyName: [{ required: true, message: '请输入企业名称', trigger: 'blur' }],
      demandName: [{ required: true, message: '请输入需求名称', trigger: 'blur' }],
      region: [{ required: true, message: '请选择完整的所属地区', trigger: 'change' }],
      techField: [
        {
          required: true,
          validator: (_rule, _value, callback) => {
            if (!form.emergingIndustry && !form.traditionalIndustry) {
              callback(new Error('请至少选择一个应用领域'))
            } else {
              callback()
            }
          },
          trigger: 'change'
        }
      ],
      demandType: [{ required: true, message: '请选择需求类型', trigger: 'change' }],
      description: [{ required: true, message: '请输入需求概述', trigger: 'blur' }],
      expectedProblem: [{ required: true, message: '请描述期望解决的问题', trigger: 'blur' }],
      demandTypeOther: [
        {
          validator: (_rule, value, callback) => {
            if (form.demandType === '其他' && !value?.trim()) {
              callback(new Error('请填写具体需求类型'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ]
    }

    const budgetUnitOptions = [
      { label: '元', value: '元' },
      { label: '万元', value: '万元' },
      { label: '百万元', value: '百万元' },
      { label: '亿元', value: '亿元' }
    ]

    const goBack = () => {
      router.back()
    }

    const populateFormFromApi = (d) => {
      isPopulating.value = true
      form.companyName = d.company_name || ''
      form.demandName = d.demand_name || ''

      const region = d.region
      if (region && typeof region === 'object') {
        form.province = region.province || ''
        form.city = region.city || ''
        if (form.province && form.city) {
          form.region = `${form.province} ${form.city}`
        } else {
          form.region = form.province || ''
        }
      } else if (typeof region === 'string') {
        form.region = region
      }

      const techFields = Array.isArray(d.tech_fields) ? d.tech_fields : []
      form.emergingIndustry = ''
      form.traditionalIndustry = ''
      techFields.forEach(f => {
        if (emergingIndustries.includes(f)) form.emergingIndustry = f
        else if (traditionalIndustries.includes(f)) form.traditionalIndustry = f
      })

      const demandTypes = Array.isArray(d.demand_types) ? d.demand_types : []
      let demandType = ''
      let demandTypeOther = ''
      demandTypes.forEach(t => {
        if (demandTypeOptions.includes(t)) demandType = t
        else demandTypeOther = t
      })
      if (d.demand_types_other) demandTypeOther = d.demand_types_other
      form.demandType = demandType
      form.demandTypeOther = demandTypeOther

      const desc = d.description || {}
      form.description = desc.overview || ''
      form.expectedProblem = desc.target_problems || ''
      form.budget = desc.budget != null ? desc.budget : null
      form.budgetUnit = '万元'
      isPopulating.value = false
    }

    const loadEditData = async (id) => {
      if (!id) return
      dataLoading.value = true
      try {
        const response = await request.get(`/api/publish/requirement/${id}`)
        if (response.code === 200 && response.data) {
          populateFormFromApi(response.data)
        } else {
          ElMessage.error(response.msg || '加载需求数据失败')
        }
      } catch (error) {
        console.error('加载需求数据失败:', error)
        ElMessage.error('加载需求数据失败')
      } finally {
        dataLoading.value = false
      }
    }

    watch(() => props.editId, (id) => {
      if (id) loadEditData(id)
    })

    onMounted(() => {
      if (props.editId) loadEditData(props.editId)
    })

    const buildAdminPayload = () => {
      const techFields = []
      if (form.emergingIndustry) techFields.push(form.emergingIndustry)
      if (form.traditionalIndustry) techFields.push(form.traditionalIndustry)
      const demandTypes = form.demandType ? [form.demandType] : []

      return {
        demand_name: form.demandName,
        company_name: form.companyName,
        tech_fields: techFields,
        tech_fields_other: '',
        demand_types: demandTypes,
        demand_types_other: form.demandType === '其他' ? (form.demandTypeOther || '') : '',
        region: { province: form.province || '', city: form.city || '' },
        description: {
          overview: form.description,
          target_problems: form.expectedProblem,
          budget: form.budget ? parseFloat(form.budget) : 0
        }
      }
    }

    const submitForm = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
      } catch {
        ElMessage.warning('请填写所有必填项')
        return
      }

      const confirmMessage = props.isAdminEdit
        ? '确认保存需求修改？'
        : '确认提交需求信息进行审核？'
      const confirmTitle = props.isAdminEdit ? '保存确认' : '提交确认'

      try {
        await ElMessageBox.confirm(
          confirmMessage,
          confirmTitle,
          { confirmButtonText: '确认', cancelButtonText: '取消', type: 'info' }
        )
      } catch {
        return
      }

      loading.value = true
      const techFields = []
      if (form.emergingIndustry) techFields.push(form.emergingIndustry)
      if (form.traditionalIndustry) techFields.push(form.traditionalIndustry)

      try {
        let response
        if (props.isAdminEdit && props.editId) {
          response = await request.put(`/api/publish/admin/requirement/${props.editId}`, buildAdminPayload())
        } else {
          response = await request.post('/api/publish/requirement', {
            ...form,
            tech_fields: techFields,
            demandTypes: form.demandType ? [form.demandType] : [],
            budget: form.budget ? parseFloat(form.budget) : 0
          })
        }

        if (response.code === 200) {
          if (props.isAdminEdit) {
            ElMessage.success('需求更新成功')
          } else {
            ElMessage.success('提交成功！您的需求信息已进入审核流程，我们将在 1-3 个工作日内完成审核。')
          }
          emit('success', response.data)
          if (!props.isAdminEdit) {
            formRef.value.resetFields()
            form.emergingIndustry = ''
            form.traditionalIndustry = ''
            form.demandTypeOther = ''
            form.budget = null
            form.budgetUnit = '万元'
            form.province = ''
            form.city = ''
            form.region = ''
          }
        } else {
          ElMessage.error(`${props.isAdminEdit ? '保存' : '提交'}失败：${response.msg || '未知错误'}`)
        }
      } catch (error) {
        console.error('提交需求失败:', error)
        ElMessage.error((props.isAdminEdit ? '保存' : '提交') + '失败：' + (error.message || '网络错误'))
      } finally {
        loading.value = false
      }
    }

    return {
      formRef,
      form,
      rules,
      budgetUnitOptions,
      provinces,
      cities,
      isMunicipality,
      goBack,
      submitForm,
      ArrowLeft,
      loading,
      dataLoading
    }
  }
}
</script>

<style scoped>
/* 样式部分保持不变，直接沿用 */
.form-loading { text-align: center; padding: 60px 20px; color: #666; font-size: 15px; }
.require-page { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); min-height: calc(100vh - 70px); padding: 30px 20px; }
.require-container { max-width: 1000px; margin: 0 auto; background: white; border-radius: 8px; padding: 30px 40px; box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08); }
.top-bar { display: flex; justify-content: flex-start; align-items: center; margin-bottom: 30px; gap: 20px; }
.form-title { text-align: left; font-size: 28px; color: #333; letter-spacing: 2px; margin: 0; flex: 1; }
.section-title { font-size: 20px; font-weight: bold; color: #333; margin: 30px 0 20px 0; padding-bottom: 10px; border-bottom: 2px solid #1890ff; }
.form-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
.form-table th, .form-table td { border: 2px solid #333; padding: 12px; text-align: left; vertical-align: top; }
.form-table th { background: #f5f7fa; font-weight: bold; color: #333; width: 180px; vertical-align: middle; }
.required { color: #ff4d4f; margin-right: 4px; }
.table-form-item { margin-bottom: 0 !important; position: relative; }
.table-form-item :deep(.el-input__wrapper) { padding-right: 0; }
.table-form-item :deep(.el-form-item__error) { display: none; }
.table-form-item :deep(.is-error .el-input__inner::placeholder),
.table-form-item :deep(.is-error .el-textarea__inner::placeholder),
.table-form-item :deep(.is-error .el-select .el-input__inner::placeholder),
.table-form-item :deep(.is-error .el-select .el-select__placeholder) { color: #f56c6c; opacity: 0.8; }
.notes-section { margin-top: 30px; padding: 20px; background: #fafafa; border-radius: 4px; }
.notes-title { font-size: 16px; color: #666; margin-bottom: 15px; font-weight: bold; }
.notes-list { list-style: none; counter-reset: note-counter; padding: 0; }
.notes-list li { position: relative; padding-left: 30px; margin-bottom: 10px; color: #666; font-size: 14px; line-height: 1.8; }
.notes-list li::before { counter-increment: note-counter; content: counter(note-counter) "."; position: absolute; left: 0; color: #999; }
.bottom-actions { text-align: center; margin-top: 40px; display: flex; justify-content: center; gap: 20px; }
.form-table td { position: relative; }
.table-form-item :deep(.el-form-item__content) { padding: 0 !important; margin-left: 0 !important; }
.form-table td :deep(.el-input),
.form-table td :deep(.el-select),
.form-table td :deep(.el-textarea),
.form-table td :deep(.el-input-number) { width: 100% !important; box-sizing: border-box; }
.form-table td :deep(.el-checkbox-group),
.form-table td :deep(.el-radio-group) { flex: 1; min-width: 0; box-sizing: border-box; }
.form-table td :deep(.el-textarea__inner) { width: 100% !important; box-sizing: border-box; }
.form-table td :deep(.el-input__wrapper) { width: 100% !important; box-sizing: border-box; }
.region-selectors { display: flex; align-items: center; gap: 10px; }
.region-selectors :deep(.el-select) { width: auto !important; flex: 1; min-width: 250px; }
.form-table td .table-form-item { width: 100%; }

/* 应用领域分组样式 */
.industry-group { display: flex; flex-direction: column; gap: 16px; }
.industry-category { border: 1px solid #e8e8e8; border-radius: 8px; padding: 14px; }
.category-title { font-size: 14px; font-weight: 600; color: #1890ff; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px dashed #f0f0f0; }
.industry-category :deep(.el-radio-group) { display: flex; flex-wrap: wrap; gap: 8px; }
.industry-category :deep(.el-radio) { margin-right: 0; white-space: nowrap; }

/* 响应式布局 */
@media (max-width: 1024px) {
  .require-container { padding: 24px 28px; }
  .form-title { font-size: 24px; }
  .section-title { font-size: 18px; }
  .form-table th { width: 150px; }
}

@media (max-width: 768px) {
  .require-page { padding: 16px 12px; }
  .require-container { padding: 20px 16px; border-radius: 6px; }
  .top-bar { flex-direction: column; align-items: flex-start; gap: 12px; }
  .form-title { font-size: 20px; letter-spacing: 1px; }
  .section-title { font-size: 16px; margin: 20px 0 14px 0; }
  .form-table,
  .form-table tbody,
  .form-table tr,
  .form-table th,
  .form-table td { display: block; width: 100% !important; box-sizing: border-box; }
  .form-table tr { margin-bottom: 12px; }
  .form-table th { width: 100% !important; background: #f5f7fa; border-bottom: none; }
  .form-table td { border-top: none; }
  .notes-section { padding: 14px; }
  .notes-list li { font-size: 13px; padding-left: 24px; }
  .bottom-actions { flex-direction: column; gap: 12px; margin-top: 28px; }
  .bottom-actions .el-button { width: 100%; }
  .region-selectors { flex-direction: column; align-items: stretch; gap: 8px; }
  .region-selectors :deep(.el-select) { min-width: 0; width: 100% !important; }
  .form-table td :deep(.el-input-number) { width: 100% !important; }
  .form-table td div[style*="flex"] { flex-direction: column; align-items: stretch !important; gap: 8px !important; }
  .form-table td div[style*="flex"] .el-input-number { width: 100% !important; }
  .form-table td div[style*="flex"] .el-select { width: 100% !important; }
}

@media (max-width: 480px) {
  .require-page { padding: 10px 8px; }
  .require-container { padding: 14px 10px; border-radius: 4px; box-shadow: 0 1px 6px rgba(0, 0, 0, 0.06); }
  .form-title { font-size: 18px; }
  .section-title { font-size: 15px; margin: 16px 0 10px 0; padding-bottom: 6px; }
  .form-table th, .form-table td { padding: 8px; }
  .notes-section { padding: 10px; margin-top: 20px; }
  .notes-title { font-size: 14px; margin-bottom: 10px; }
  .notes-list li { font-size: 12px; padding-left: 20px; margin-bottom: 6px; }
  .bottom-actions { margin-top: 22px; }
}
</style>