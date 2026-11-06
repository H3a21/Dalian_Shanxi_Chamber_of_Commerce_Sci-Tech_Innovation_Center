<template>
  <div class="publish-page">
    <div v-if="dataLoading" class="form-loading">加载中...</div>
    <div class="publish-container" v-show="!dataLoading">
      <div class="top-bar" v-if="!isDialog">
        <el-button @click="goBack" :icon="ArrowLeft">返回</el-button>
        <h1 class="form-title">《成果采集表》</h1>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="left" label-width="160px" class="publish-form">
        <div class="section-title">一、成果基本信息</div>
        <table class="form-table">
          <tbody>
          <tr>
            <th><span class="required">*</span> 成果名称</th>
            <td>
              <el-form-item prop="name" class="table-form-item">
                <el-input v-model="form.name" placeholder="请输入完整成果名称" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 成果持有人</th>
            <td>
              <el-form-item prop="holder" class="table-form-item">
                <el-input v-model="form.holder" placeholder="高校/科研院所/企业/团队负责人" />
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
            <th><span class="required">*</span> 技术领域</th>
            <td>
              <el-form-item prop="techField" class="table-form-item">
                <el-select v-model="form.techField" placeholder="--请选择--">
                  <el-option v-for="item in techFieldOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
              <el-form-item v-if="form.techField === '其他'" prop="techFieldOther" class="table-form-item">
                <el-input v-model="form.techFieldOther" placeholder="请填写具体领域" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 技术成熟度</th>
            <td>
              <el-form-item prop="maturity" class="table-form-item">
                <el-select v-model="form.maturity" placeholder="--请选择--">
                  <el-option label="实验室理论阶段" value="实验室理论阶段" />
                  <el-option label="中试阶段" value="中试阶段" />
                  <el-option label="可规模量产" value="可规模量产" />
                </el-select>
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th><span class="required">*</span> 转化方式</th>
            <td>
              <el-form-item prop="transformTypes" class="table-form-item">
                <el-checkbox-group v-model="form.transformTypes">
                  <div class="checkbox-vertical">
                    <el-checkbox label="技术转让" value="技术转让" />
                    <el-checkbox label="技术许可" value="技术许可" />
                    <el-checkbox label="技术入股" value="技术入股" />
                    <el-checkbox label="合作开发" value="合作开发" />
                    <el-checkbox label="其他" value="其他" />
                  </div>
                </el-checkbox-group>
                <el-input v-if="form.transformTypes.includes('其他')" v-model="form.transformOther" placeholder="请填写具体转化方式" style="margin-top: 8px; width: 300px;" />
              </el-form-item>
            </td>
          </tr>
          </tbody>
        </table>

        <div class="section-title">二、成果描述</div>
        <table class="form-table">
          <tbody>
          <tr>
            <th><span class="required">*</span> 成果摘要</th>
            <td>
              <el-form-item prop="summary" class="table-form-item">
                <el-input v-model="form.summary" type="textarea" :rows="4" placeholder="请简要描述成果的主要内容" />
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th>技术优势描述</th>
            <td>
              <div style="margin-bottom: 15px;">
                <div class="field-label">创新性：</div>
                <el-radio-group v-model="form.innovationLevel">
                  <el-radio value="国际领先">国际领先</el-radio>
                  <el-radio value="国内领先">国内领先</el-radio>
                  <el-radio value="行业领先">行业领先</el-radio>
                </el-radio-group>
              </div>
              <div>
                <div class="field-label">与现有技术相比的优势：</div>
                <el-input v-model="form.advantages" type="textarea" :rows="3" placeholder="请描述与现有技术相比的优势" />
              </div>
            </td>
          </tr>
          <tr>
            <th>核心技术指标</th>
            <td>
              <el-input v-model="form.techIndicators" type="textarea" :rows="3" placeholder="请填写核心技术指标" />
            </td>
          </tr>
          <tr>
            <th>获得的知识产权</th>
            <td>
              <el-input v-model="form.intellectualProperty" type="textarea" :rows="3" placeholder="请填写已获得的知识产权情况（专利、软件著作权等）" />
            </td>
          </tr>
          </tbody>
        </table>

        <div class="section-title">三、成果转化</div>
        <table class="form-table">
          <tbody>
          <tr>
            <th><span class="required">*</span> 合作方式偏好</th>
            <td>
              <el-form-item prop="cooperationPref" class="table-form-item">
                <el-radio-group v-model="form.cooperationPref">
                  <div class="checkbox-vertical">
                    <div class="radio-with-extra">
                      <el-radio value="技术转让">技术转让</el-radio>
                      <span v-if="form.cooperationPref === '技术转让'" class="extra-input">
                        （转让费：期望 <el-input-number v-model="form.transferFee" :precision="2" :controls="false" placeholder="" size="small" style="width: 120px;" /> 万元）
                      </span>
                    </div>
                    <div class="radio-with-extra">
                      <el-radio value="技术许可">技术许可</el-radio>
                      <span v-if="form.cooperationPref === '技术许可'" class="extra-input">
                        （许可方式：
                        <el-radio-group v-model="form.licenseType" size="small">
                          <el-radio value="独占">独占</el-radio>
                          <el-radio value="排他">排他</el-radio>
                          <el-radio value="普通">普通</el-radio>
                        </el-radio-group>
                        ）
                      </span>
                    </div>
                    <div class="radio-with-extra">
                      <el-radio value="技术入股">技术入股</el-radio>
                      <span v-if="form.cooperationPref === '技术入股'" class="extra-input">
                        （作价 <el-input-number v-model="form.equityValue" :precision="2" :controls="false" placeholder="" size="small" style="width: 120px;" /> 万元，占 <el-input-number v-model="form.equityPercent" :controls="false" :min="0" :max="100" :precision="2" :step="0.1" placeholder="" size="small" style="width: 100px;" @change="onEquityPercentChange" /> 股%）
                      </span>
                    </div>
                    <el-radio value="合作开发">合作开发</el-radio>
                    <div class="radio-with-extra">
                      <el-radio value="其他">其他</el-radio>
                      <el-input v-if="form.cooperationPref === '其他'" v-model="form.cooperationOther" placeholder="请填写" style="width: 200px; margin-left: 8px;" size="small" />
                    </div>
                  </div>
                </el-radio-group>
              </el-form-item>
            </td>
          </tr>
          <tr>
            <th>期望转化时间</th>
            <td>
              <div class="inline-row">
                <el-date-picker v-model="form.expectDate" type="month" placeholder="选择月份" format="YYYY年M月" class="expect-date-picker" />
                <span style="color: #666; white-space: nowrap;">前完成转化</span>
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
          <li>审核结果将通过站内信或短信通知，审核通过后自动在"成果中心"展示。</li>
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
  name: 'PublishView',
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

    const techFieldOptions = [
      '新一代信息技术', '生物医药与健康', '航空航天',
      '新材料', '高技术服务', '新能源与节能', '资源与环境',
      '先进制造与自动化', '现代农业', '海洋技术', '其他'
    ]

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
      name: '',
      holder: '',
      province: '',
      city: '',
      region: '',
      techField: '',
      techFieldOther: '',
      maturity: '',
      transformTypes: [],
      transformOther: '',
      summary: '',
      innovationLevel: '',
      advantages: '',
      techIndicators: '',
      intellectualProperty: '',
      cooperationPref: '',
      transferFee: null,
      licenseType: '',
      equityValue: null,
      equityPercent: null,
      cooperationOther: '',
      expectDate: null
    })

    // 计算当前省份对应的城市列表
    const cities = computed(() => {
      if (form.province && citiesMap[form.province]) {
        return citiesMap[form.province]
      }
      return []
    })

    // 判断是否为直辖市
    const isMunicipality = computed(() => {
      return form.province && ['北京市', '天津市', '上海市', '重庆市'].includes(form.province)
    })

    // 监听省份变化，重置城市选择
    watch(() => form.province, (newProvince) => {
      if (isPopulating.value) return
      form.city = ''
      // 自动更新region字段
      form.region = newProvince
    })

    // 监听城市变化，更新region字段
    watch(() => form.city, (newCity) => {
      if (form.province && newCity) {
        form.region = form.province + ' ' + newCity
      } else if (form.province) {
        form.region = form.province
      } else {
        form.region = ''
      }
    })

    // 监听技术领域变化，清理自定义内容
    watch(() => form.techField, (newVal, oldVal) => {
      if (oldVal === '其他' && newVal !== '其他') {
        form.techFieldOther = ''
      }
    })

    // 监听转化方式变化，清理自定义内容和相关字段
    // 【修改点1】：使用 [...form.transformTypes] 返回一个新数组，这样 oldVal 和 newVal 就是独立的了
    watch(() => [...form.transformTypes], (newVal, oldVal) => {
      const wasOther = oldVal?.includes('其他') || false
      const isOther = newVal?.includes('其他') || false
      if (wasOther && !isOther) {
        form.transformOther = ''
      }

      // 检查被取消的选项，清理相关字段
      if (oldVal) {
        const removedOptions = oldVal.filter(item => !newVal.includes(item))
        removedOptions.forEach(option => {
          // 清理多余数据
          if (option === '技术转让') {
            form.transferFee = null
          } else if (option === '技术许可') {
            form.licenseType = ''
          } else if (option === '技术入股') {
            form.equityValue = null
            form.equityPercent = null
          }
          
          // 【修改点2】：如果取消的正好是当前的“合作方式偏好”，同步将其清空
          if (form.cooperationPref === option) {
            form.cooperationPref = ''
          }
        })
      }
    }) // 【修改点3】：去掉了 { deep: true }，因为解构数组本身就会触发更新

    const rules = {
      name: [{ required: true, message: '请输入成果名称', trigger: 'blur' }],
      holder: [{ required: true, message: '请输入成果持有人', trigger: 'blur' }],
      region: [{ required: true, message: '请选择完整的所属地区', trigger: 'change' }],
      techField: [{ required: true, message: '请选择技术领域', trigger: 'change' }],
      techFieldOther: [
        {
          validator: (_rule, value, callback) => {
            if (form.techField === '其他' && !value?.trim()) {
              callback(new Error('请填写技术领域自定义内容'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ],
      maturity: [{ required: true, message: '请选择技术成熟度', trigger: 'change' }],
      transformTypes: [{ type: 'array', required: true, min: 1, message: '请至少选择一种转化方式', trigger: 'change' }],
      summary: [{ required: true, message: '请输入成果摘要', trigger: 'blur' }],
      cooperationPref: [{ required: true, message: '请选择合作方式偏好', trigger: 'change' }]
    }

    // 监听合作方式偏好变化，同步到转化方式多选并清理旧选项数据
    watch(() => form.cooperationPref, (newVal, oldVal) => {
      const validOptions = ['技术转让', '技术许可', '技术入股', '合作开发']

      if (oldVal) {
        if (oldVal === '技术转让') {
          form.transferFee = null
        } else if (oldVal === '技术许可') {
          form.licenseType = ''
        } else if (oldVal === '技术入股') {
          form.equityValue = null
          form.equityPercent = null
        } else if (oldVal === '其他') {
          form.cooperationOther = ''
        }
      }

      if (newVal === '其他') {
        if (!form.transformTypes.includes('其他')) {
          form.transformTypes.push('其他')
        }
      } else if (newVal && validOptions.includes(newVal)) {
        const otherIndex = form.transformTypes.indexOf('其他')
        if (otherIndex > -1) {
          form.transformTypes.splice(otherIndex, 1)
        }
        if (!form.transformTypes.includes(newVal)) {
          form.transformTypes.push(newVal)
        }
      }
    })

    const goBack = () => {
      router.back()
    }

    const populateFormFromApi = (d) => {
      isPopulating.value = true
      form.name = d.achievement_name || d.title || ''
      form.holder = d.owner || d.holder || ''

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

      const techFields = d.tech_fields || d.technologyFields || []
      const techOther = d.tech_fields_other || d.otherTechnologyField || ''
      if (techFields.includes('其他') || (techOther && !techFields.some(f => f && f !== '其他'))) {
        form.techField = '其他'
        form.techFieldOther = techOther
      } else if (techFields.length > 0) {
        form.techField = techFields[0]
        form.techFieldOther = ''
      }

      form.maturity = d.tech_maturity || d.maturity || ''
      form.transformTypes = [...(d.transfer_methods || d.transferMethods || [])]
      const transferOther = d.transfer_methods_other || d.otherTransferMethod || ''
      if (transferOther) {
        if (!form.transformTypes.includes('其他')) {
          form.transformTypes.push('其他')
        }
        form.transformOther = transferOther
      }

      const desc = d.description || {}
      form.summary = desc.summary || d.summary || ''
      form.innovationLevel = desc.innovation_level || d.innovationLevel || ''
      form.advantages = desc.advantages || d.advantages || ''
      form.techIndicators = desc.core_indicators || d.coreTechnicalIndicators || ''
      form.intellectualProperty = desc.intellectual_property || d.intellectualProperties || ''

      const tp = d.transfer_preference || {}
      const preferred = tp.preferred_method || ''
      if (preferred) {
        form.cooperationPref = preferred
      } else if (tp.tech_transfer?.enabled) {
        form.cooperationPref = '技术转让'
      } else if (tp.tech_license?.enabled) {
        form.cooperationPref = '技术许可'
      } else if (tp.tech_investment?.enabled) {
        form.cooperationPref = '技术入股'
      } else if (tp.cooperation_dev) {
        form.cooperationPref = '合作开发'
      } else if (tp.other) {
        form.cooperationPref = '其他'
      } else {
        form.cooperationPref = ''
      }

      form.transferFee = tp.tech_transfer?.expected_fee ?? d.techTransferFee ?? null
      form.licenseType = tp.tech_license?.type || d.licenseType || ''
      form.equityValue = tp.tech_investment?.valuation ?? d.techValuation ?? null
      form.equityPercent = tp.tech_investment?.share_ratio ?? d.equityPercentage ?? null
      form.cooperationOther = tp.other || d.otherCollaborationPreference || ''

      const expectedDate = tp.expected_complete_date
      if (expectedDate?.year && expectedDate?.month) {
        form.expectDate = new Date(expectedDate.year, expectedDate.month - 1, 1)
      } else {
        form.expectDate = null
      }
      isPopulating.value = false
    }

    const loadEditData = async (id) => {
      if (!id) return
      dataLoading.value = true
      try {
        const response = await request.get(`/api/publish/achievement/${id}`)
        if (response.code === 200 && response.data) {
          populateFormFromApi(response.data)
        } else {
          ElMessage.error(response.msg || '加载成果数据失败')
        }
      } catch (error) {
        console.error('加载成果数据失败:', error)
        ElMessage.error('加载成果数据失败')
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
      const techFieldVal = form.techField
      const cooperationPref = form.cooperationPref
      return {
        achievement_name: form.name,
        owner: form.holder,
        tech_fields: techFieldVal === '其他' ? ['其他'] : (techFieldVal ? [techFieldVal] : []),
        tech_fields_other: techFieldVal === '其他' ? (form.techFieldOther || '') : '',
        tech_maturity: form.maturity,
        transfer_methods: form.transformTypes.filter(t => t !== '其他'),
        transfer_methods_other: form.transformOther || '',
        region: { province: form.province || '', city: form.city || '' },
        description: {
          summary: form.summary,
          innovation_level: form.innovationLevel,
          advantages: form.advantages,
          core_indicators: form.techIndicators,
          intellectual_property: form.intellectualProperty
        },
        transfer_preference: {
          tech_transfer: {
            enabled: cooperationPref === '技术转让',
            expected_fee: form.transferFee || 0
          },
          tech_license: {
            enabled: cooperationPref === '技术许可',
            type: form.licenseType || ''
          },
          tech_investment: {
            enabled: cooperationPref === '技术入股',
            valuation: form.equityValue || 0,
            share_ratio: form.equityPercent || 0
          },
          cooperation_dev: cooperationPref === '合作开发',
          other: cooperationPref === '其他' ? (form.cooperationOther || '') : '',
          preferred_method: cooperationPref,
          expected_complete_date: form.expectDate
            ? { year: form.expectDate.getFullYear(), month: form.expectDate.getMonth() + 1 }
            : {}
        }
      }
    }

    const onEquityPercentChange = (val) => {
      if (val === null || val === undefined || val === '') {
        form.equityPercent = null
        return
      }
      if (val < 0) form.equityPercent = 0
      else if (val > 100) form.equityPercent = 100
    }

    const submitForm = async () => {
      if (!formRef.value) return

      try {
        await formRef.value.validate()
      } catch {
        ElMessage.warning('请填写所有必填项')
        return
      }

      if (form.transformTypes.includes('其他') && !form.transformOther.trim()) {
        ElMessage.warning('请填写转化方式自定义内容')
        return
      }
      if (form.cooperationPref === '其他' && !form.cooperationOther.trim()) {
        ElMessage.warning('请填写合作方式偏好自定义内容')
        return
      }

      const confirmMessage = props.isAdminEdit
        ? '确认保存成果修改？'
        : '确认提交成果信息进行审核？'
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
      try {
        let response
        if (props.isAdminEdit && props.editId) {
          response = await request.put(`/api/publish/admin/achievement/${props.editId}`, buildAdminPayload())
        } else {
          response = await request.post('/api/publish/achievement', {
            ...form,
            transformTypes: form.transformTypes,
            expectDate: form.expectDate ? form.expectDate : null
          })
        }

        if (response.code === 200) {
          if (props.isAdminEdit) {
            ElMessage.success('成果更新成功')
          } else {
            ElMessage.success('提交成功！您的成果信息已进入审核流程，我们将在 1-3 个工作日内完成审核。')
          }
          emit('success', response.data)
          if (!props.isAdminEdit) {
            formRef.value.resetFields()
            form.techFieldOther = ''
            form.transformOther = ''
            form.cooperationOther = ''
            form.innovationLevel = ''
            form.advantages = ''
            form.techIndicators = ''
            form.intellectualProperty = ''
            form.transferFee = null
            form.licenseType = ''
            form.equityValue = null
            form.equityPercent = null
            form.expectDate = null
            form.province = ''
            form.city = ''
            form.region = ''
          }
        } else {
          ElMessage.error(`${props.isAdminEdit ? '保存' : '提交'}失败：${response.msg || '未知错误'}`)
        }
      } catch (error) {
        console.error('提交成果失败:', error)
        ElMessage.error((props.isAdminEdit ? '保存' : '提交') + '失败：' + (error.message || '网络错误'))
      } finally {
        loading.value = false
      }
    }

    return {
      formRef,
      form,
      rules,
      techFieldOptions,
      provinces,
      cities,
      isMunicipality,
      goBack,
      submitForm,
      onEquityPercentChange,
      ArrowLeft,
      loading,
      dataLoading
    }
  }
}
</script>

<style scoped>
/* 样式部分保持不变，由于代码较长且未作修改，此处直接沿用你的原样式即可 */
.form-loading {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 15px;
}

.publish-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: calc(100vh - 70px);
  padding: 30px 20px;
}
.publish-container {
  max-width: 1000px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 30px 40px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}
.top-bar {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 30px;
  gap: 20px;
}
.form-title {
  text-align: left;
  font-size: 28px;
  color: #333;
  letter-spacing: 2px;
  margin: 0;
  flex: 1;
}
.section-title {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin: 30px 0 20px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid #1890ff;
}
.form-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}
.form-table th, .form-table td {
  border: 2px solid #333;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}
.form-table th {
  background: #f5f7fa;
  font-weight: bold;
  color: #333;
  width: 180px;
  vertical-align: middle;
}
.required { color: #ff4d4f; margin-right: 4px; }
.table-form-item { margin-bottom: 0 !important; position: relative; }
.table-form-item :deep(.el-input__wrapper) { padding-right: 0; }
.table-form-item :deep(.el-form-item__error) { display: none; }
.table-form-item :deep(.is-error .el-input__inner::placeholder),
.table-form-item :deep(.is-error .el-textarea__inner::placeholder),
.table-form-item :deep(.is-error .el-select .el-input__inner::placeholder),
.table-form-item :deep(.is-error .el-select .el-select__placeholder) { color: #f56c6c; opacity: 0.8; }
.checkbox-vertical { display: flex; flex-direction: column; gap: 10px; }
.checkbox-vertical :deep(.el-checkbox) { height: auto; }
.radio-with-extra { display: flex; align-items: center; flex-wrap: nowrap; gap: 4px; }
.extra-input { display: inline-flex; align-items: center; gap: 4px; color: #333; font-size: 14px; white-space: nowrap; }
.inline-row { display: flex; align-items: center; gap: 0; flex-wrap: nowrap; }
.inline-row :deep(.el-date-picker) { margin-right: 0; }
.expect-date-picker { width: 120px !important; }
.expect-date-picker :deep(.el-input__wrapper) { width: 100% !important; }
.field-label { font-weight: bold; color: #333; margin-bottom: 8px; }
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
.form-table td :deep(.el-radio-group) { width: 100%; box-sizing: border-box; }
.form-table td :deep(.el-textarea__inner) { width: 100% !important; box-sizing: border-box; }
.form-table td :deep(.el-input__wrapper) { width: 100% !important; box-sizing: border-box; }
.radio-with-extra :deep(.el-input-number),
.radio-with-extra :deep(.el-input),
.radio-with-extra :deep(.el-input__wrapper),
.extra-input :deep(.el-input-number),
.extra-input :deep(.el-radio-group) { width: auto !important; }
.region-selectors { display: flex; align-items: center; gap: 10px; }
.region-selectors :deep(.el-select) { width: auto !important; flex: 1; min-width: 250px; }
.inline-row :deep(.el-input),
.inline-row :deep(.el-input__wrapper) { width: auto !important; }
/* ========== Responsive ========== */

@media (max-width: 1024px) {
  .publish-container {
    padding: 25px 30px;
  }
  .form-title {
    font-size: 24px;
  }
  .section-title {
    font-size: 18px;
  }
  .form-table th {
    width: 150px;
  }
  .region-selectors :deep(.el-select) {
    min-width: 200px;
  }
}

@media (max-width: 768px) {
  .publish-page {
    padding: 20px 15px;
  }
  .publish-container {
    padding: 20px;
    border-radius: 6px;
  }
  .top-bar {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  .form-title {
    font-size: 22px;
  }
  .section-title {
    font-size: 17px;
    margin: 20px 0 15px 0;
  }
  .form-table th {
    width: 130px;
    padding: 10px 8px;
  }
  .form-table td {
    padding: 10px 8px;
  }
  .region-selectors {
    flex-direction: column;
    gap: 8px;
  }
  .region-selectors :deep(.el-select) {
    min-width: unset;
    width: 100%;
  }
  .radio-with-extra {
    flex-wrap: wrap;
  }
  .bottom-actions {
    flex-direction: column;
    gap: 12px;
  }
  .bottom-actions :deep(.el-button) {
    width: 100%;
  }
  .notes-section {
    padding: 15px;
  }
  .inline-row {
    flex-wrap: wrap;
    gap: 4px;
  }
}

@media (max-width: 480px) {
  .publish-page {
    padding: 15px 8px;
    min-height: calc(100vh - 60px);
  }
  .publish-container {
    padding: 12px;
    border-radius: 4px;
  }
  .top-bar {
    margin-bottom: 20px;
  }
  .form-title {
    font-size: 18px;
  }
  .section-title {
    font-size: 15px;
    margin: 15px 0 12px 0;
  }
  .form-table th,
  .form-table td {
    padding: 8px 6px;
    font-size: 13px;
  }
  .form-table th {
    width: 100px;
  }
  .notes-section {
    padding: 10px;
  }
  .notes-title {
    font-size: 14px;
  }
  .notes-list li {
    font-size: 13px;
    padding-left: 24px;
  }
  .expect-date-picker {
    width: 100px !important;
  }
  .extra-input {
    font-size: 12px;
    white-space: normal;
  }
  .checkbox-vertical {
    gap: 6px;
  }
  .field-label {
    font-size: 13px;
  }
  .inline-row {
    flex-wrap: wrap;
    gap: 4px;
  }
}
</style>