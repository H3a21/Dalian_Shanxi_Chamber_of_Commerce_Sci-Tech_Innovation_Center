<template>
  <div class="auth-page">
    <main id="auth-page" class="page-section active">
      <div class="auth-layout">
        <div class="auth-card">
          <div class="auth-tabs">
            <div class="auth-tab" :class="{ active: activeTab === 'login' }" @click="switchAuthTab('login')">登录</div>
            <div class="auth-tab" :class="{ active: activeTab === 'register' }" @click="switchAuthTab('register')">用户注册</div>
          </div>

          <!-- 登录表单 -->
          <div class="auth-form" :class="{ active: activeTab === 'login' }">
            <div class="input-group" :class="{ error: loginErrors.account }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                <input type="text" placeholder="请输入用户名/手机号" v-model="loginForm.account" @keyup.enter="handleLogin">
              </div>
              <div class="error-msg" v-if="loginErrors.account">{{ loginErrors.account }}</div>
            </div>
            <div class="input-group" :class="{ error: loginErrors.password }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <input type="password" placeholder="请输入密码" v-model="loginForm.password" @keyup.enter="handleLogin">
              </div>
              <div class="error-msg" v-if="loginErrors.password">{{ loginErrors.password }}</div>
            </div>
            <div class="forgot-pwd">
              <a href="javascript:;" @click="$router.push('/forgot-password')">忘记密码</a>
            </div>
            <button class="submit-btn" @click="handleLogin" :disabled="loginLoading">
              {{ loginLoading ? '登录中...' : '登录' }}
            </button>
          </div>

          <!-- 注册表单 -->
          <div class="auth-form" :class="{ active: activeTab === 'register' }">
            <div class="input-group" :class="{ error: registerErrors.phone }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="2" width="14" height="20" rx="2" ry="2"></rect><line x1="12" y1="18" x2="12.01" y2="18"></line></svg>
                <input type="text" placeholder="请输入手机号" v-model="registerForm.phone" @input="validatePhone">
              </div>
              <div class="error-msg" v-if="registerErrors.phone">{{ registerErrors.phone }}</div>
            </div>
            <div class="input-group verify-group" :class="{ error: registerErrors.code }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                <input type="text" placeholder="请输入验证码" v-model="registerForm.code">
              </div>
              <button class="get-code-btn" @click="sendRegisterCode" :disabled="registerCodeDisabled">
                {{ registerCodeBtnText }}
              </button>
              <div class="error-msg" v-if="registerErrors.code">{{ registerErrors.code }}</div>
            </div>
            <div class="input-group" :class="{ error: registerErrors.password }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <input type="password" placeholder="请输入密码" v-model="registerForm.password" @input="validatePassword('register')">
              </div>
              <div class="error-msg" v-if="registerErrors.password">{{ registerErrors.password }}</div>
            </div>
            <div class="input-group" :class="{ error: registerErrors.confirm }">
              <div class="input-wrapper">
                <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                <input type="password" placeholder="请确认密码" v-model="registerForm.confirm" @input="validateConfirm('register')">
              </div>
              <div class="error-msg" v-if="registerErrors.confirm">{{ registerErrors.confirm }}</div>
            </div>
            <div class="agreement">
              <input type="checkbox" id="agree" v-model="registerForm.agree">
              <label for="agree">我已阅读并同意 <a href="javascript:;" @click.prevent="showAgreement = true">《用户服务协议》</a></label>
              <div class="error-msg" v-if="registerErrors.agree">{{ registerErrors.agree }}</div>
            </div>
            <button class="submit-btn" @click="handleRegister" :disabled="registerLoading">
              {{ registerLoading ? '注册中...' : '注册' }}
            </button>
          </div>

        </div>
      </div>
    </main>

    <!-- 用户服务协议弹窗 -->
    <div class="agreement-overlay" v-if="showAgreement" @click.self="showAgreement = false">
      <div class="agreement-modal">
        <div class="agreement-modal-header">
          <h2>大连山西商会科创中心用户服务协议</h2>
          <button class="agreement-close-btn" @click="showAgreement = false">&times;</button>
        </div>
        <div class="agreement-modal-body">
          <div class="agreement-section">
            <p class="version-row">版本更新日期：2026年4月19日 &nbsp; | &nbsp; 版本生效日期：2026年4月26日</p>

            <p class="text-indent">尊敬的用户：欢迎您使用大连山西商会科创中心平台（以下简称"本平台"或"我们"）。本平台是由大连山西商会合法拥有并运营的，专注于科技成果转化、企业需求对接及专家智库服务的线上服务平台。为保障您的合法权益，请您在注册或使用本平台服务前，务必审慎阅读、充分理解本协议各条款内容，特别是免除或限制责任的条款、法律适用和争议解决条款。免除或限制责任的条款将以粗体下划线标识，您应重点阅读。</p>
            <p class="text-indent"><strong>特别提示：</strong>您在注册过程中点击"同意"按钮，即表示您已充分阅读、理解并接受本协议的全部内容，确认承担由此产生的一切法律后果。若您不同意本协议的任何条款，请立即停止注册程序。</p>

            <div class="section-divider"></div>

            <h3>一、服务条款的确认及接受</h3>
            <p><strong>1.1</strong> 主体资格：本平台各项电子服务的所有权和运作权归大连山西商会及其授权的运营主体所有。本平台将完全按照本协议及平台发布的各项操作规则严格执行。</p>
            <p><strong>1.2</strong> 协议生效：您确认所有服务条款并完成注册程序时，本协议在您与本平台间成立并立即发生法律效力。</p>
            <p><strong>1.3</strong> 补充协议与规则：本平台的《隐私政策》、《金融服务用户须知》、《电子签章服务协议》、《专家入驻协议》、各项平台规则、各类公告及针对特定服务发布的单独协议均为本协议不可分割的组成部分，与本协议具有同等法律效力。您使用特定服务（如金融服务申请、专家预约、电子签章等），即视为您同意并接受相关的单独协议。</p>
            <p><strong>1.4</strong> 协议变更：根据法律法规变化及平台运营需要，本平台有权对本协议条款进行修改。修改后的条款一经在本平台公布即生效并替代原有条款。您应不时关注本平台公告及协议变动。如您不同意更新后的内容，应立即停止使用本平台；如您继续使用，即视为您知悉变更并同意接受。</p>

            <h3>二、服务须知</h3>
            <p><strong>2.1</strong> 服务内容：本平台运用自身开发的操作系统，通过互联网为用户提供包括但不限于"成果中心"、"需求中心"、"专家中心"、"合作伙伴"、"金融服务"等板块的信息展示、检索、对接及资讯服务。平台服务可能随业务调整而变化，具体以平台实际提供为准。</p>
            <p><strong>2.2</strong> 硬件与网络要求：使用本平台服务，您需自行配备上网所需设备（如电脑、手机、平板等），并承担个人上网所支付的电话费、网络流量费等相关费用。</p>
            <p><strong>2.3</strong> 软件获取与更新：您应当通过本平台官方网站或我们授权的第三方应用市场下载最新版本客户端。为了改善体验及安全需求，本平台将不定期提供软件更新。新版本发布后，旧版本软件可能无法正常使用或存在安全漏洞，本平台不保证旧版本的持续可用性，请您及时更新至最新版本。</p>

            <h3>三、账户注册、管理及使用</h3>
            <p><strong>3.1</strong> 用户资格：您确认在注册使用本平台服务前，您具备中华人民共和国法律规定的与您行为相适应的民事行为能力。若您为未成年人或限制民事行为能力人，需在监护人的监护及同意下注册使用。若您代表企业或机构注册，您应确保已获得该单位的充分授权。</p>
            <p><strong>3.2</strong> 注册信息真实性：您承诺在注册时按照平台提示提供真实、准确、完整及最新的手机号码、身份信息或企业资质信息。若您的资料存在虚假、盗用或未及时更新，导致的一切后果及法律责任由您自行承担，本平台有权终止服务并注销账户。</p>
            <p><strong>3.3</strong> 账户安全保管：您的账户仅限于您本人/本单位使用。您应妥善保管账户密码、验证码及用于登录的设备。任何通过您的账户进行的操作（包括发布成果、发起需求、签署电子合同）均视为您本人的真实意思表示，由此产生的风险及损失由您自行承担。</p>
            <p><strong>3.4</strong> 实名认证与权限：鉴于科创对接的严肃性与安全性，本平台有权要求使用特定高级功能（如发布专利成果、申请金融服务、使用电子签章）的用户完成严格的实名认证（个人身份证件核验或企业营业执照核验）。未完成实名认证或认证未通过的用户，将无法使用相应功能。</p>
            <p><strong>3.5</strong> 未成年人保护</p>
            <p class="sub-p">1. 未成年人注册使用本平台服务，必须在监护人的监护及同意下进行。监护人应承担未成年人使用平台服务的全部责任。</p>
            <p class="sub-p">2. 若本平台发现有未成年人未经监护人同意注册使用本平台服务，有权立即注销其账户。</p>
            <p class="sub-p">3. 监护人发现未成年人擅自使用本平台服务的，可联系平台客服申请注销账户。</p>

            <h3>四、平台服务规范及订单对接</h3>
            <p><strong>4.1</strong> 信息展示与对接：本平台仅作为信息发布与对接的场所。您在"成果中心"上传的专利、技术说明，或在"需求中心"发布的技术瓶颈，仅代表您单方的合作意愿。本平台对用户发布的信息仅进行形式合规性审核，不对信息的真实性、准确性、完整性、技术可行性及商业价值作出任何明示或默示的担保。</p>
            <p><strong>4.2</strong> 交易独立：用户之间基于本平台获取信息后进行的线下洽谈、技术转让、样品寄送、款项支付等行为，均为独立的法律行为。本平台不是买卖合同、技术合同或服务合同的相对方，不对交易双方的资信、技术先进性、交付成果、履约能力承担任何明示或默示的担保责任。因交易产生的一切风险、损失及法律责任，均由交易双方自行承担。</p>
            <p><strong>4.3</strong> 知识产权声明：您在平台上传的成果图片、技术方案描述，其知识产权仍归您或原权利人所有。您在此授予本平台一项免费的、不可撤销的、全球范围内的非独占使用许可，仅用于在平台页面内展示、推广您发布的信息（如推荐至首页、成果榜单、行业资讯），以增加对接成功率。本平台不得将上述内容用于任何商业盈利目的。</p>
            <p><strong>4.4</strong> 平台收费规则</p>
            <p class="sub-p">1. 本平台基础信息浏览、检索服务永久免费。针对平台提供的精准对接、专家预约、电子签章、金融服务中介、成果转化代理等增值服务，本平台有权收取相应的服务费或佣金。</p>
            <p class="sub-p">2. 具体收费标准、支付方式、结算周期将在平台对应服务页面公示或通过单独协议约定。本平台有权根据业务发展调整收费标准，调整后的标准将提前7个工作日在平台公示，公示期满后生效。</p>
            <p class="sub-p">3. 若因用户单方面原因取消已确认的增值服务订单，已支付的服务费不予退还；因平台原因导致服务无法提供的，平台将全额退还已收取的费用。</p>
            <p><strong>4.5</strong> 订单对接与确认</p>
            <p class="sub-p">1. 用户通过平台发起的对接申请、服务预约等订单，经对方确认后即成立具有法律约束力的预约合同。</p>
            <p class="sub-p">2. 平台将通过短信、APP推送等方式向双方发送订单确认通知，通知内容视为合同的组成部分。</p>
            <p><strong>4.6</strong> 电子合同与签章</p>
            <p class="sub-p">1. 本平台提供的电子签章服务符合《中华人民共和国电子签名法》规定，通过本平台签署的电子合同与纸质合同具有同等法律效力。</p>
            <p class="sub-p">2. 电子签章仅可由完成实名认证的账户持有人本人使用。您应妥善保管电子签章的使用权限，任何通过您的账户完成的电子签章操作均视为您本人的真实意思表示，由此产生的法律责任由您自行承担。</p>
            <p class="sub-p">3. 本平台将对电子合同的签署过程、签署内容及签署时间进行完整存证，存证期限不少于合同履行完毕后3年。在合同纠纷中，本平台将依法提供存证证明。</p>
            <p class="sub-p">4. 若您发现电子签章被冒用或盗用，应立即通知本平台冻结账户及签章权限。本平台在收到通知并核实身份后，将采取必要的补救措施，但对冒用或盗用发生在通知前的损失不承担责任。</p>
            <p><strong>4.7</strong> 纠纷协助义务</p>
            <p class="sub-p">1. 用户之间发生交易或服务纠纷时，可向本平台申请调解。本平台将基于中立立场，协助双方沟通协商，但不承担任何调解结果的担保责任。</p>
            <p class="sub-p">2. 本平台有权根据纠纷处理需要，向双方调取相关证据，并在法律法规允许的范围内向司法机关提供必要的协助。</p>

            <h3>五、用户个人信息保护及授权</h3>
            <p><strong>5.1</strong> 隐私保护：保护您的个人信息是本平台的核心准则。我们将严格按照《中华人民共和国个人信息保护法》《大连山西商会科创中心隐私政策》收集、存储、使用及保护您的信息。本协议附件及平台公示的隐私政策详细说明了我们对信息的处理规则，建议您完整阅读隐私政策。</p>
            <p><strong>5.2</strong> 信息收集范围：在您使用注册、浏览、发布、对接功能时，我们会收集必要的个人信息（如手机号、姓名、地理位置、企业基本信息）。如您拒绝提供必要信息，将无法使用本平台的基本功能。使用金融服务等敏感功能时，我们将根据法律法规要求收集您的身份信息、银行账户信息等敏感个人信息，并采取加密存储等特殊保护措施。</p>
            <p><strong>5.3</strong> 信息共享与授权：</p>
            <p class="sub-p">• 为促进对接：您同意我们将您在平台上公开的成果简介、需求标题、专家领域及联系方式（您自行选择公开的部分）共享给平台内的注册用户或潜在意向方，以实现精准匹配。</p>
            <p class="sub-p">• 法律合规披露：为配合行政监管机关、司法机关的合法要求，在法律法规允许的范围内，本平台有权依法提供您的相关注册信息及行为日志。</p>
            <p class="sub-p">• 服务委托：我们可能委托第三方服务商提供技术支持、支付结算等服务，仅会向第三方提供必要的信息，并要求第三方严格遵守保密义务，不得将信息用于任何其他目的。</p>
            <p><strong>5.4</strong> 商业信息退订：您有权通过注册时填写的手机号接收与平台相关的服务通知、活动推荐等商业信息。如您不希望接收此类信息，可通过短信回复"TD"或在APP设置中关闭消息推送。</p>
            <p><strong>5.5</strong> 数据安全保障</p>
            <p class="sub-p">1. 本平台将采取符合行业标准的技术措施和管理制度，保护您的个人信息安全，防止信息泄露、篡改、丢失。</p>
            <p class="sub-p">2. 若发生或可能发生个人信息安全事件，本平台将立即启动应急预案，采取补救措施，并按照法律法规要求及时通知您和相关监管部门。通知方式包括但不限于短信、APP推送、电子邮件或平台公告。</p>
            <p><strong>5.6</strong> 用户数据权利</p>
            <p class="sub-p">1. 您有权查阅、复制、更正、补充您在本平台的个人信息。您可通过账户设置页面自行操作，或联系平台客服协助处理。</p>
            <p class="sub-p">2. 您有权请求删除您的个人信息。在您注销账户后，本平台将删除您的个人信息或进行匿名化处理，但法律法规另有规定的除外。</p>
            <p class="sub-p">3. 您有权撤回对个人信息处理的同意。撤回同意后，本平台将停止处理您的相关信息，但不影响此前基于您的同意已进行的信息处理活动的合法性。</p>
            <p class="sub-p">4. 本平台将在收到您的权利请求后15个工作日内作出答复。</p>
            <p><strong>5.7</strong> 数据留存期限</p>
            <p class="sub-p">1. 您的账户信息将在您使用平台服务期间持续留存，直至您注销账户。</p>
            <p class="sub-p">2. 您发布的公开信息将在您删除或注销账户后立即从平台展示页面移除，但为了履行法律义务、解决纠纷或保障交易安全，本平台可能会保留相关信息至必要期限届满。</p>

            <h3>六、用户行为规范</h3>
            <p><strong>6.1</strong> 禁止发布内容：您在使用本平台过程中，严禁制作、复制、发布、传播含有下列内容的信息：</p>
            <p class="sub-p">- 反对宪法所确定的基本原则，危害国家安全，泄露国家秘密的；</p>
            <p class="sub-p">- 损害国家荣誉和利益，破坏民族团结或国家宗教政策的；</p>
            <p class="sub-p">- 虚假、欺诈、夸大其词的技术成果或需求描述；</p>
            <p class="sub-p">- 侵犯他人知识产权、商业秘密、个人隐私或肖像权的；</p>
            <p class="sub-p">- 含有病毒、木马、爬虫等恶意程序，或干扰平台正常运营、窃取平台数据的。</p>
            <p><strong>6.2</strong> 交易秩序维护：您不得利用平台进行炒作、虚假交易、恶意评价或套取平台补贴。不得通过任何手段恶意注册账户以规避平台规则。</p>
            <p><strong>6.3</strong> 违规处理措施：若您违反本协议或平台规则，本平台有权视情节严重程度采取以下一项或多项措施：</p>
            <p class="sub-p">1. 警告并责令限期整改；</p>
            <p class="sub-p">2. 限制账户部分功能（如暂停发布、屏蔽内容、禁止对接）；</p>
            <p class="sub-p">3. 冻结账户及关联账户的资产及对接权限；</p>
            <p class="sub-p">4. 永久封禁账户，清空违规数据并拒绝再次提供服务；</p>
            <p class="sub-p">5. 向相关监管部门或司法机关举报。</p>

            <h3>七、免责声明</h3>
            <p><strong>7.1</strong> 信息真实性免责：本平台虽致力于审核发布内容的合规性，但因互联网信息的海量性及技术手段限制，本平台无法逐一实质性核实每一个用户发布的成果、需求的真实性与可靠性。您应对您在平台获取的信息自行尽到合理注意义务，并自行承担据此决策的风险。若您发现虚假信息，可向本平台举报，本平台将在核实后及时处理。</p>
            <p><strong>7.2</strong> 不可抗力及系统维护：因网络攻击、机房故障、系统升级、法律法规政策调整或自然灾害等不可抗力导致服务中断或数据丢失的，本平台将在恢复后尽力采取补救措施，但对此类非因平台故意或重大过失导致的损失不承担责任。本平台将提前24小时通过平台公告通知计划性系统维护。</p>
            <p><strong>7.3</strong> 第三方链接：本平台页面可能包含指向合作伙伴的链接，此类链接的运营由第三方独立负责，本平台对第三方网站的内容、隐私政策或交易行为不承担任何责任。您在访问第三方网站时应自行阅读其服务协议和隐私政策。</p>
            <p><strong>7.4</strong> 平台错误信息免责：本平台将尽力保证平台信息的准确性，但对于因技术故障、第三方数据提供错误等非平台故意原因导致的信息错误，本平台不承担责任。若您发现错误信息，可通知本平台，本平台将在核实后及时更正。</p>

            <h3>八、知识产权</h3>
            <p><strong>8.1</strong> 平台权利：本平台的Logo、页面设计、程序代码、数据库结构、数据分析模型及平台自产内容，其知识产权归大连山西商会所有，未经书面许可，任何人不得复制、模仿、镜像或反向工程。</p>
            <p><strong>8.2</strong> 侵权投诉：若您认为平台内其他用户发布的内容侵犯了您的合法权益，请通过官方客服邮箱发送权利证明及初步证据，我们将在法律规定的期限内进行处理。</p>
            <p><strong>8.3</strong> 知识产权侵权处理流程</p>
            <p class="sub-p">1. 投诉方应向本平台提交以下材料：</p>
            <p class="sub-sub-p">• 权利人的身份证明文件（个人身份证或企业营业执照）；</p>
            <p class="sub-sub-p">• 权利证明文件（专利证书、著作权登记证书、商标注册证等）；</p>
            <p class="sub-sub-p">• 侵权内容的具体链接及侵权说明；</p>
            <p class="sub-sub-p">• 权利人的联系方式及地址。</p>
            <p class="sub-p">2. 本平台收到符合要求的投诉材料后，将在3个工作日内对投诉内容进行初步审核，并将投诉材料转送给被投诉方。</p>
            <p class="sub-p">3. 被投诉方收到投诉材料后，有权在5个工作日内提交反通知及相关证据。反通知应包含被投诉方的身份证明、不侵权的证明材料及联系方式。</p>
            <p class="sub-p">4. 本平台收到被投诉方的反通知后，将在3个工作日内将反通知转送给投诉方。投诉方未在10个工作日内提交司法机关或行政机关的受理通知的，本平台将恢复被删除的内容。</p>
            <p class="sub-p">5. 本平台仅对投诉材料进行形式审核，不对侵权事实作出实质性判断。因错误投诉导致被投诉方损失的，由投诉方承担全部赔偿责任。</p>
            <p><strong>8.4</strong> 平台免责：本平台根据法律法规规定采取的删除、屏蔽等措施，不承担任何法律责任。对于权利人因错误通知造成的损失，本平台不承担连带责任。</p>

            <h3>九、协议的终止与法律适用</h3>
            <p><strong>9.1</strong> 终止情形：</p>
            <p class="sub-p">• 用户主动申请注销账户并经平台审核通过；</p>
            <p class="sub-p">• 用户违反本协议规定，被平台依据规则强制注销账户；</p>
            <p class="sub-p">• 平台根据业务调整公告终止服务。</p>
            <p><strong>9.2</strong> 协议终止后的处理</p>
            <p class="sub-p">1. 协议终止后，您的账户将被注销，您将无法继续使用本平台的任何服务。</p>
            <p class="sub-p">2. 协议终止前已产生的权利义务不受影响，双方仍应履行完毕。</p>
            <p class="sub-p">3. 本协议中关于知识产权、免责声明、争议解决等条款在协议终止后仍然有效。</p>
            <p><strong>9.3</strong> 法律适用：本协议的订立、执行、解释及争议解决均适用中华人民共和国法律（仅为本协议之目的，不包含香港、澳门及台湾地区法律）。</p>
            <p><strong>9.4</strong> 争议解决：因本协议产生的或与之相关的任何争议，双方应首先友好协商解决；协商不成的，任何一方均有权将争议提交至大连仲裁委员会，按照该会届时有效的仲裁规则进行仲裁。仲裁裁决是终局的，对双方均具有约束力。</p>

            <h3>十、专家服务专项规则</h3>
            <p><strong>10.1</strong> 专家资质审核</p>
            <p class="sub-p">1. 本平台对申请入驻的专家实行严格的资质审核制度，审核内容包括但不限于学历、职称、工作经历、科研成果、行业影响力等。</p>
            <p class="sub-p">2. 专家应保证其提供的资质证明文件真实、准确、完整。若专家提供虚假信息，本平台有权立即取消其专家资格，并永久封禁其账户。</p>
            <p class="sub-p">3. 本平台将定期对专家资质进行复核，对于不再符合入驻条件的专家，本平台有权取消其专家资格。</p>
            <p><strong>10.2</strong> 专家服务规范</p>
            <p class="sub-p">1. 专家应按照平台规定的服务流程和标准提供服务，保证服务质量和专业性。</p>
            <p class="sub-p">2. 专家不得提供虚假、误导性的技术意见或建议，不得泄露用户的商业秘密或技术秘密。</p>
            <p class="sub-p">3. 专家不得私下与用户进行交易，不得收取用户任何形式的额外费用。</p>
            <p><strong>10.3</strong> 服务评价与纠纷处理</p>
            <p class="sub-p">1. 用户在接受专家服务后，有权对服务质量进行评价。评价结果将作为专家考核的重要依据。</p>
            <p class="sub-p">2. 若用户对专家服务不满意，可向本平台投诉。本平台将在收到投诉后7个工作日内进行调查处理。</p>
            <p class="sub-p">3. 因专家提供错误意见或建议导致用户损失的，由专家本人承担全部赔偿责任。本平台仅在收取的服务费范围内承担补充赔偿责任。</p>
            <p><strong>10.4</strong> 专家退出机制</p>
            <p class="sub-p">1. 专家可主动申请退出本平台，经平台审核通过后，其专家资格终止。</p>
            <p class="sub-p">2. 专家违反本协议或平台规则的，本平台有权视情节严重程度采取警告、限制服务、取消专家资格等措施。</p>

            <h3>十一、金融服务专项规则</h3>
            <p><strong>11.1</strong> 服务性质声明</p>
            <p class="sub-p">1. 本平台仅为用户与金融机构之间提供信息对接服务，不直接提供金融产品或金融服务，不参与金融机构的任何经营活动。</p>
            <p class="sub-p">2. 本平台展示的金融产品信息均由合作金融机构提供，本平台不对金融产品的真实性、准确性、合法性作出任何担保。</p>
            <p><strong>11.2</strong> 金融机构资质公示</p>
            <p class="sub-p">1. 本平台将在显著位置公示合作金融机构的营业执照、金融许可证等资质文件。</p>
            <p class="sub-p">2. 用户应自行核实金融机构的资质及金融产品的风险，谨慎做出投资或融资决策。</p>
            <p><strong>11.3</strong> 风险提示</p>
            <p class="sub-p">1. 金融服务存在风险，包括但不限于信用风险、市场风险、流动性风险等。用户应根据自身的风险承受能力，自主判断并承担相应的风险。</p>
            <p class="sub-p">2. 本平台将在金融产品展示页面进行充分的风险提示，用户在申请金融服务前应仔细阅读风险提示书。</p>
            <p><strong>11.4</strong> 金融信息保护</p>
            <p class="sub-p">1. 本平台将对用户的金融敏感信息（如银行账户信息、征信信息）采取严格的保密措施，未经用户书面同意，不得向任何第三方泄露。</p>
            <p class="sub-p">2. 本平台仅会向合作金融机构提供必要的用户信息，用于金融服务的审核和办理。</p>
            <p><strong>11.5</strong> 禁止性规定</p>
            <p class="sub-p">1. 禁止用户利用本平台进行非法集资、洗钱、诈骗等违法犯罪活动。</p>
            <p class="sub-p">2. 禁止金融机构通过本平台发布虚假金融产品信息或进行误导性宣传。</p>

            <div class="section-divider"></div>
            <p class="signature">大连山西商会科创中心 法务部</p>
            <p class="agree-confirm">[ 我已阅读并同意《用户服务协议》及《隐私政策》 ]</p>
          </div>
        </div>
        <div class="agreement-modal-footer">
          <button class="btn-agree" @click="registerForm.agree = true; showAgreement = false">我已阅读并同意</button>
          <button class="btn-close-modal" @click="showAgreement = false">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import useAuth from '../composables/useAuth'

const route = useRoute()
const router = useRouter()
const auth = useAuth()

const activeTab = ref('login')
const redirect = computed(() => route.query.redirect || '')

// 登录表单
const loginForm = reactive({
  account: '',
  password: ''
})
const loginErrors = reactive({
  account: '',
  password: ''
})
const loginLoading = ref(false)

// 注册表单
const registerForm = reactive({
  phone: '',
  code: '',
  password: '',
  confirm: '',
  agree: false
})
const registerErrors = reactive({
  phone: '',
  code: '',
  password: '',
  confirm: '',
  agree: ''
})
const registerLoading = ref(false)
const registerCodeDisabled = ref(false)
const registerCodeCountdown = ref(0)
const phoneCheckTimer = ref(null)
const registerCodeBtnText = computed(() => {
  if (registerCodeCountdown.value > 0) {
    return `${registerCodeCountdown.value}秒后重新获取`
  }
  return '获取验证码'
})

const showAgreement = ref(false)


// 根据路由query切换tab
onMounted(() => {
  updateActiveTabFromQuery()
})

watch(() => route.query.tab, (newTab) => {
  if (newTab === 'login' || newTab === 'register') {
    activeTab.value = newTab
  } else {
    activeTab.value = 'login'
  }
})

function updateActiveTabFromQuery() {
  const tab = route.query.tab
  if (tab === 'login' || tab === 'register') {
    activeTab.value = tab
  } else {
    activeTab.value = 'login'
  }
}

function switchAuthTab(type) {
  activeTab.value = type
  const query = { tab: type }
  if (route.query.redirect) {
    query.redirect = route.query.redirect
  }
  router.replace({
    path: '/auth',
    query
  })
}

// 验证手机号
function validatePhone() {
  if (!registerForm.phone) {
    registerErrors.phone = '请输入手机号'
    return
  } else if (!/^1\d{10}$/.test(registerForm.phone)) {
    registerErrors.phone = '手机号格式不正确'
    return
  } else {
    registerErrors.phone = ''
  }

  // 防抖检查手机号是否已注册
  if (phoneCheckTimer.value) {
    clearTimeout(phoneCheckTimer.value)
    phoneCheckTimer.value = null
  }

  phoneCheckTimer.value = setTimeout(async () => {
    // 防止手机号被清空后发送请求
    if (!registerForm.phone || !/^1\d{10}$/.test(registerForm.phone)) {
      return
    }
    const res = await auth.checkPhoneRegistered(registerForm.phone)
    if (res.success && res.registered) {
      registerErrors.phone = '该手机号已注册，请直接登录'
    } else if (!res.success) {
      // 检查失败，不显示错误，避免干扰用户
      console.error('检查手机号失败:', res.message)
    }
  }, 500)
}

// 验证密码
function validatePassword() {
  if (!registerForm.password) {
    registerErrors.password = '请输入密码'
  } else if (registerForm.password.length < 6) {
    registerErrors.password = '密码长度至少6位'
  } else {
    registerErrors.password = ''
  }
}

// 验证确认密码
function validateConfirm() {
  if (!registerForm.confirm) {
    registerErrors.confirm = '请确认密码'
  } else if (registerForm.password !== registerForm.confirm) {
    registerErrors.confirm = '两次输入的密码不一致'
  } else {
    registerErrors.confirm = ''
  }
}

// 发送注册验证码
async function sendRegisterCode() {
  validatePhone()
  if (registerErrors.phone) return

  registerCodeDisabled.value = true
  registerCodeCountdown.value = 60

  const res = await auth.sendSmsCode(registerForm.phone, 'register')
  if (res.success) {
    // 开始倒计时
    const timer = setInterval(() => {
      registerCodeCountdown.value--
      if (registerCodeCountdown.value <= 0) {
        clearInterval(timer)
        registerCodeDisabled.value = false
      }
    }, 1000)
  } else {
    registerCodeDisabled.value = false
    registerCodeCountdown.value = 0
  }
}


// 处理登录
async function handleLogin() {
  // 清除错误
  loginErrors.account = ''
  loginErrors.password = ''

  const account = loginForm.account.trim()
  if (!account) {
    loginErrors.account = '请输入用户名/手机号'
    return
  }
  if (!loginForm.password) {
    loginErrors.password = '请输入密码'
    return
  }

  // 如果输入的是手机号格式，检查是否已注册
  if (/^1\d{10}$/.test(account)) {
    const checkRes = await auth.checkPhoneRegistered(account)
    if (checkRes.success && !checkRes.registered) {
      loginErrors.account = '手机号未注册服务，请先注册'
      return
    }
    // 如果检查失败（网络错误等），继续尝试登录，后端会验证
  }

  loginLoading.value = true
  const res = await auth.login(account, loginForm.password)
  loginLoading.value = false

  if (res.success) {
    // 登录成功，跳转到redirect参数指定的路径或首页
    const target = redirect.value || '/'
    router.push(target)
  } else {
    // 登录失败，显示错误信息
    // 后端可能返回"密码错误"或"账号或密码错误"
    if (res.message && res.message.includes('密码')) {
      // 如果是密码相关错误，显示在密码输入框下方
      loginErrors.password = res.message
    } else if (res.message && (res.message.includes('账号') || res.message.includes('手机号'))) {
      // 如果是账号相关错误，显示在账号输入框下方
      loginErrors.account = res.message
    }
    // ElMessage已经在拦截器中显示，这里不需要重复显示
  }
}

// 处理注册
async function handleRegister() {
  // 验证
  validatePhone()
  validatePassword()
  validateConfirm()
  registerErrors.code = ''

 // 修改这里：增加清空错误状态的逻辑
  if (!registerForm.code) {
    registerErrors.code = '请输入验证码'
    return
  } else {
    registerErrors.code = '' // 填了验证码，清空错误
  }
  
  if (!registerForm.agree) {
    registerErrors.agree = '请同意用户服务协议'
    return
  } else {
    registerErrors.agree = '' // 勾选了协议，清空错误
  }

  // 如果有错误，停止
  if (registerErrors.phone || registerErrors.password || registerErrors.confirm || registerErrors.code) {
    return
  }

  registerLoading.value = true
  const res = await auth.register(registerForm.phone, registerForm.password, registerForm.code, '')
  registerLoading.value = false

  if (res.success) {
    // 注册成功，切换到登录tab
    switchAuthTab('login')
    // 清空表单
    registerForm.phone = ''
    registerForm.code = ''
    registerForm.password = ''
    registerForm.confirm = ''
    registerForm.agree = false
  }
}

</script>

<style scoped>
/* ================= 登录/注册页面样式 ================= */
.auth-layout {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 70px);
  padding: 20px;
}
.auth-card {
  background: var(--white);
  width: 100%;
  max-width: 400px;
  padding: 25px;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
}

/* 顶部选项卡切换 */
.auth-tabs {
  display: flex;
  background-color: #f6f8fb;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}
.auth-tab {
  flex: 1;
  text-align: center;
  padding: 12px 0;
  font-size: 15px;
  color: #888;
  cursor: pointer;
  transition: all 0.3s;
}
.auth-tab.active {
  background-color: var(--white);
  color: var(--theme-blue);
  font-weight: bold;
  border-bottom: 3px solid var(--theme-blue);
  box-shadow: 0 2px 5px rgba(0,0,0,0.02);
}

/* 表单内容区 */
.auth-form { display: none; }
.auth-form.active { display: block; }

.input-group {
  position: relative;
  margin-bottom: 20px;
  padding-bottom: 0;
}

.input-wrapper {
  position: relative;
}

/* 图标定位 */
.input-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 16px;
  height: 16px;
  color: #c0c4cc;
}

/* 输入框样式 */
.input-group input[type="text"],
.input-group input[type="password"] {
  width: 100%;
  padding: 12px 15px 12px 45px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  color: var(--text-main);
  outline: none;
  transition: border-color 0.3s;
}

.input-group input:focus {
  border-color: var(--theme-blue);
}

/* 错误状态 */
.input-group.error input {
  border-color: #ff4d4f;
}
.input-group.error .input-icon {
  color: #ff4d4f;
}
.error-msg {
  color: #ff4d4f;
  font-size: 12px;
  position: absolute;
  top: 100%;
  left: 42px;
  margin-top: 2px;
}
.verify-group .error-msg {
  left: 0;
  padding-left: 42px;
}

/* 忘记密码 */
.forgot-pwd {
  display: flex;
  justify-content: flex-end;
  margin-top: -8px;
  margin-bottom: 12px;
}
.forgot-pwd a {
  font-size: 14px;
  color: var(--theme-blue);
  cursor: pointer;
}

/* 获取验证码组 */
.verify-group {
  display: flex;
  gap: 12px;
}
.verify-group .input-wrapper {
  flex: 1;
}
.verify-group input {
  width: 100%;
}
.get-code-btn {
  background-color: transparent;
  color: var(--theme-blue);
  border: 1px solid var(--theme-blue);
  border-radius: 4px;
  padding: 0 15px;
  cursor: pointer;
  font-size: 14px;
  white-space: nowrap;
  transition: all 0.3s;
}
.get-code-btn:hover:not(:disabled) {
  background-color: #e6f7ff;
}
.get-code-btn:disabled {
  color: #ccc;
  border-color: #ccc;
  cursor: not-allowed;
}

/* 协议勾选 */
.agreement {
  display: flex;
  align-items: center;
  font-size: 13px;
  color: #999;
  margin-bottom: 15px;
  position: relative;
}
.agreement input[type="checkbox"] {
  margin-right: 8px;
  cursor: pointer;
  width: 14px;
  height: 14px;
}
.agreement a { color: var(--theme-blue); }
.agreement .error-msg {
  position: absolute;
  top: 100%;
  left: 0;
  margin-top: 2px;
}

/* 提交大按钮 */
.submit-btn {
  width: 100%;
  background-color: var(--theme-blue);
  color: var(--white);
  border: none;
  padding: 12px;
  border-radius: 30px;
  font-size: 15px;
  cursor: pointer;
  letter-spacing: 1px;
  transition: background-color 0.3s;
}
.submit-btn:hover:not(:disabled) {
  background-color: #0073e6;
}
.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .auth-layout {
    padding: 12px;
    min-height: calc(100vh - 60px);
  }
  .auth-card {
    max-width: 100%;
    padding: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
  }
  .auth-tab {
    padding: 10px 0;
    font-size: 14px;
  }
  .input-group input[type="text"],
  .input-group input[type="password"] {
    padding: 10px 14px 10px 40px;
    font-size: 14px;
  }
  .verify-group {
    flex-direction: column;
    gap: 8px;
  }
  .get-code-btn {
    padding: 10px;
    width: 100%;
    text-align: center;
  }
  .error-msg {
    left: 0;
    padding-left: 0;
  }
  .verify-group .error-msg {
    padding-left: 0;
  }
  .agreement {
    font-size: 12px;
  }
  .submit-btn {
    padding: 10px;
    font-size: 14px;
  }
  .agreement-modal {
    max-width: 100%;
    max-height: 90vh;
    margin: 0 12px;
  }
  .agreement-modal-header {
    padding: 16px 20px 12px;
  }
  .agreement-modal-body {
    padding: 16px 20px;
  }
  .agreement-modal-footer {
    padding: 12px 20px 16px;
    flex-direction: column;
    gap: 8px;
  }
  .btn-agree, .btn-close-modal {
    width: 100%;
    min-width: auto;
  }
}

@media (max-width: 480px) {
  .auth-card {
    padding: 16px;
  }
  .auth-layout {
    padding: 8px;
  }
  .input-group {
    margin-bottom: 16px;
  }
  .input-group input[type="text"],
  .input-group input[type="password"] {
    padding: 8px 12px 8px 36px;
    font-size: 13px;
  }
}

/* ================= 用户服务协议弹窗 ================= */
.agreement-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.55);
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  animation: overlayFadeIn 0.2s ease;
}

@keyframes overlayFadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.agreement-modal {
  background: white;
  width: 100%;
  max-width: 780px;
  max-height: 85vh;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  animation: modalSlideIn 0.25s ease;
}

@keyframes modalSlideIn {
  from { opacity: 0; transform: translateY(30px); }
  to { opacity: 1; transform: translateY(0); }
}

.agreement-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px 16px;
  border-bottom: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.agreement-modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  letter-spacing: 0.5px;
}

.agreement-close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f5f5f5;
  border-radius: 50%;
  font-size: 20px;
  line-height: 32px;
  text-align: center;
  cursor: pointer;
  color: #999;
  transition: all 0.2s;
  padding: 0;
}

.agreement-close-btn:hover {
  background: #e8e8e8;
  color: #333;
}

.agreement-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px 28px;
  scrollbar-width: thin;
  scrollbar-color: #d9d9d9 transparent;
}

.agreement-modal-body::-webkit-scrollbar {
  width: 6px;
}

.agreement-modal-body::-webkit-scrollbar-track {
  background: transparent;
}

.agreement-modal-body::-webkit-scrollbar-thumb {
  background: #d9d9d9;
  border-radius: 3px;
}

.agreement-section .version-row {
  text-align: center;
  color: rgba(0, 0, 0, 0.45);
  font-size: 13px;
  margin-bottom: 20px;
}

.agreement-section p.text-indent {
  text-indent: 2em;
  margin-bottom: 12px;
}

.agreement-section .section-divider {
  height: 1px;
  background: #f0f0f0;
  margin: 16px 0;
}

.agreement-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: rgba(0, 0, 0, 0.85);
  margin-top: 20px;
  margin-bottom: 10px;
  padding-bottom: 6px;
  border-bottom: 1px solid #f5f5f5;
}

.agreement-section > p {
  font-size: 14px;
  line-height: 1.75;
  color: rgba(0, 0, 0, 0.65);
  margin-bottom: 8px;
}

.agreement-section > p strong {
  color: rgba(0, 0, 0, 0.85);
  font-weight: 600;
}

.agreement-section p.sub-p {
  font-size: 14px;
  line-height: 1.75;
  color: rgba(0, 0, 0, 0.62);
  margin-bottom: 4px;
  padding-left: 1.5em;
}

.agreement-section p.sub-sub-p {
  font-size: 14px;
  line-height: 1.75;
  color: rgba(0, 0, 0, 0.6);
  margin-bottom: 2px;
  padding-left: 3em;
}

.agreement-section .signature {
  text-align: right;
  font-size: 14px;
  color: rgba(0, 0, 0, 0.85);
  margin-top: 16px;
  margin-bottom: 8px;
}

.agreement-section .agree-confirm {
  text-align: center;
  font-size: 14px;
  color: var(--theme-blue);
  font-weight: 500;
  padding: 12px;
  background: #f0f9ff;
  border-radius: 6px;
  margin-top: 8px;
}

.agreement-modal-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 16px 28px 20px;
  border-top: 1px solid #f0f0f0;
  flex-shrink: 0;
}

.btn-agree {
  min-width: 160px;
  padding: 10px 28px;
  background: var(--theme-blue);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-agree:hover {
  background: #0073e6;
}

.btn-close-modal {
  min-width: 100px;
  padding: 10px 20px;
  background: white;
  color: rgba(0, 0, 0, 0.65);
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close-modal:hover {
  color: var(--theme-blue);
  border-color: var(--theme-blue);
}
</style>