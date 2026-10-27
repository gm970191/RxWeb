import hashlib
import os
import secrets
import sqlite3
import sys

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

try:
    from app.auth import hash_password
except Exception:
    def hash_password(password: str) -> str:
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 210000)
        return f"{salt}${digest.hex()}"

# 产品模拟数据
products = [
    (1, '智能手表', 399, '智能设备', 'https://picsum.photos/240/160?1', '健康监测，消息提醒，超长续航。'),
    (2, '蓝牙耳机', 199, '音频设备', 'https://picsum.photos/240/160?2', '高清音质，降噪体验，舒适佩戴。'),
    (3, '机械键盘', 499, '外设', 'https://picsum.photos/240/160?3', 'RGB背光，手感极佳，耐用轴体。'),
    (4, '4K 显示器', 1299, '显示设备', 'https://picsum.photos/240/160?4', '超清分辨率，护眼技术，广色域。'),
    (5, '游戏鼠标', 299, '外设', 'https://picsum.photos/240/160?5', '高精度传感器，人体工学设计。'),
    (6, '智能音箱', 259, '智能设备', 'https://picsum.photos/240/160?6', '语音助手，智能家居控制。'),
    (7, '降噪耳机', 899, '音频设备', 'https://picsum.photos/240/160?7', '主动降噪，长续航。'),
    (8, '平板电脑', 1999, '智能设备', 'https://picsum.photos/240/160?8', '轻薄便携，强劲性能。'),
    (9, '电竞椅', 799, '外设', 'https://picsum.photos/240/160?9', '舒适支撑，久坐不累。'),
    (10, '无线充电器', 129, '外设', 'https://picsum.photos/240/160?10', '快速充电，兼容多设备。'),
    (11, '智能门锁', 1099, '智能设备', 'https://picsum.photos/240/160?11', '安全便捷，远程控制。'),
    (12, '蓝牙音箱', 159, '音频设备', 'https://picsum.photos/240/160?12', '小巧便携，音质出色。'),
]

# 新闻模拟数据：(id, title, date, source, summary, content)
news = [
    (1, '公司发布全新一代智能办公系统', '2024-06-20', '官方新闻',
     '新系统集成了AI助手、自动化流程和数据分析功能，旨在大幅提升企业协作效率和决策水平。',
     '瑞学软件今日正式发布全新一代智能办公系统。新版本将AI助手、自动化流程和数据分析能力整合到同一工作台，帮助企业缩短审批链路、沉淀业务知识，并让管理层更及时地看到经营指标。\n\n本次升级覆盖公文、日程、项目协同和知识库四个核心模块。用户可以在对话中直接发起待办、检索制度文件，也可以把重复性填报交给流程机器人。系统已在内部试运行三个月，平均处理时效缩短约 28%。\n\n现有客户可按合同约定免费升级；新客户可预约演示环境，由实施顾问协助完成组织和权限初始化。'),
    (2, 'RxWeb前端框架V3.0正式版发布', '2024-06-18', '技术博客',
     '经过数月的测试与优化，RxWeb前端框架V3.0正式版现已发布，带来了更快的渲染速度和更丰富的组件库。',
     '经过数月打磨，RxWeb 前端框架 V3.0 正式版已向全部开发者开放。此版本重构了渲染管线，列表和表单场景的首屏时间平均下降 35%，并补充了上传、筛选栏、移动端导航等常用组件。\n\n兼容说明：V2 项目可通过官方迁移脚本升级。主要破坏性变更集中在主题变量命名和个别表格插槽，详细清单见升级指南。我们建议先在预发环境完成回归，再切换生产。\n\n欢迎到资源下载页获取完整源码包、示例工程和接口文档。'),
    (3, '荣获"年度最具创新力软件企业"奖', '2024-06-15', '行业资讯',
     '凭借在云计算和大数据领域的突出贡献，我司被授予"年度最具创新力软件企业"奖项。',
     '在本年度软件产业评选中，瑞学软件凭借云计算与大数据方向的产品落地能力，获评“年度最具创新力软件企业”。评选委员会特别提到公司在政务协同和制造业数智化项目中的可复制方案。\n\n这是对公司研发与交付团队的共同认可。我们将继续把奖项转化为产品迭代动力，把创新用在客户真正需要的效率提升上。'),
    (4, '安全通告：请立即更新您的系统至最新版本', '2024-06-12', '安全中心',
     '我们发现了一个潜在的安全漏洞，并已在最新版本中修复。请所有用户尽快更新，以确保您的数据安全。',
     '安全中心于近日完成一轮例行审计，发现旧版本在特定权限组合下存在会话校验不足的风险。该问题已在最新补丁中修复，目前没有收到实际攻击报告。\n\n请管理员立即将系统升级到最新版本，并检查是否仍使用默认口令。补丁包可在资源下载页获取，升级过程无需停机超过 10 分钟。如需协助，请联系技术支持热线。'),
    (5, '第二季度财报发布，营收同比增长30%', '2024-06-10', '投资者关系',
     '公司第二季度财报显示，营收和利润均实现强劲增长，市场份额进一步扩大。',
     '公司发布第二季度经营情况：营业收入同比增长 30%，毛利率保持稳定，订阅制收入占比继续提升。增长主要来自智能办公续约、行业解决方案新增以及培训服务。\n\n本季度新增签约客户 46 家，其中制造业与教育行业贡献过半。公司将持续加大产品研发和客户成功投入，保持稳健扩张。'),
    (6, '成功举办第一届开发者大会', '2024-06-05', '官方新闻',
     '第一届开发者大会圆满落幕，吸引了全球上千名开发者参与，共同探讨技术的未来。',
     '第一届瑞学开发者大会已圆满落幕。两天议程覆盖框架演进、低代码实践、安全合规和大模型落地，线上线下合计超过一千名开发者参与。\n\n现场发布了插件市场预览版和三条官方示例路线。演讲资料将在会后一周内放到资源下载页，欢迎继续讨论和提交 Issue。'),
    (7, '与XXX大学达成战略合作，共建AI实验室', '2024-06-01', '合作快讯',
     '双方将共同致力于人工智能前沿技术的研究与应用，推动产学研深度融合。',
     '瑞学软件与 XXX 大学签署战略合作协议，共建人工智能联合实验室。双方将围绕文档理解、流程推荐和行业知识图谱开展课题，并设立研究生实习岗位。\n\n实验室首年计划完成两项示范应用：智能公文摘要与质检规则辅助编写。成果将优先回馈到智能办公产品线，同时支持教学案例建设。'),
    (8, '瑞学云平台正式上线，支持一键私有化部署', '2024-07-08', '产品动态',
     '企业可按自身合规要求选择公有云或本地机房，10 分钟内拉起完整演示环境。',
     '瑞学云平台即日起对受邀客户开放。平台提供应用编排、证书管理和备份策略，既支持公有云订阅，也支持在客户机房一键安装。\n\n标准演示环境可在约 10 分钟内部署完成，包含门户、新闻、产品和权限模块。后续可按模块开通数据分析与开放接口。欢迎现有客户申请升级评估。'),
    (9, '顺利通过 ISO 27001 信息安全管理体系认证', '2024-07-22', '安全中心',
     '认证覆盖研发、交付和运维全流程，为金融、政务等对安全要求更高的客户提供合规基础。',
     '公司已获得 ISO 27001 信息安全管理体系认证。审计范围覆盖需求、开发、测试、交付和运维，包括访问控制、变更管理和供应商管理等关键过程。\n\n这意味着我们能够以更规范的方式处理客户数据，并按年度接受监督审核。相关证书扫描件可向商务同事索取，用于招投标材料。'),
    (10, 'RxWeb 现已支持完整手机浏览模式', '2024-08-05', '技术博客',
     '官网与管理端在小屏设备上改为汉堡导航、单列卡片和可滑动表格，桌面版视觉保持不变。',
     '为方便客户用手机查看官网，RxWeb 增加了系统化的移动端适配：宽度小于 768 像素时自动切换汉堡菜单、单列产品卡片、新闻换行和下载资源卡片列表。\n\n桌面端原有视觉和交互不变。建议使用真机或浏览器设备模式回归导航、表单提交和分页。如发现个别页面留白异常，请把机型和截图发给支持团队。'),
    (11, '第三季度经营简报：海外业务占比首次超过 20%', '2024-09-18', '投资者关系',
     '东南亚和中东渠道开始贡献经常性收入，公司同步完善多语言与时区支持。',
     '第三季度海外业务收入占比首次超过 20%，主要来自东南亚渠道伙伴和中东地区的私有化项目。为支撑交付，产品已补齐英文界面和多时区日程。\n\n下一阶段将增加阿拉伯语预览，并在当地建立远程支持窗口。国内业务保持平稳，续约率继续高于行业平均水平。'),
    (12, '开放生态合作计划启动，首批 12 家伙伴入驻', '2024-10-12', '合作快讯',
     '咨询、实施和行业插件三类伙伴可共享商机与技术认证，共同服务区域客户。',
     '开放生态合作计划正式启动，首批 12 家伙伴完成认证，覆盖咨询、实施和行业插件三类角色。伙伴可使用沙箱环境、联调接口和联合品牌材料。\n\n计划提供分级支持：注册级可访问文档，认证级可参与商机共享，战略级可共建行业版本。欢迎有交付能力的团队报名。'),
    (13, '秋季技术沙龙回顾：大模型如何走进审批流', '2024-10-28', '官方新闻',
     '现场演示了制度问答、草稿生成和风险提示三个场景，并开放有限名额内测。',
     '秋季技术沙龙以“大模型走进审批流”为主题，演示了制度问答、公文草稿生成和敏感词风险提示。与会客户最关心幻觉控制和审计留痕，我们给出了提示词模板加人工确认的落地路径。\n\n内测名额有限，已签约智能办公的客户可向客户成功经理申请。沙龙回放将在两周内发布。'),
    (14, '客户案例：某制造集团协同效率提升 40%', '2024-11-15', '行业资讯',
     '通过统一待办、移动审批和自动归档，跨工厂单据平均处理时间从 3 天降到 1.8 天。',
     '某大型制造集团上线瑞学智能办公后，将分散在邮件和即时通讯中的审批收回统一待办。结合移动端审批和自动归档，跨工厂单据平均处理时间从 3 天降至 1.8 天，效率提升约 40%。\n\n项目还打通了 ERP 物料状态，避免“线上已批、线下缺料”的反复沟通。完整案例可向售前团队索取。'),
    (15, '2025 产品路线图：低代码与智能体双轮驱动', '2024-12-06', '产品动态',
     '明年将推出可视化流程设计器和可插拔智能体，让业务人员也能配置常见协同场景。',
     '2025 年产品将沿“低代码 + 智能体”两条线推进。上半年发布可视化流程设计器，支持拖拽节点、条件分支和超时提醒；下半年提供可插拔智能体，把问答、摘要和质检能力接到现有表单。\n\n路线图会按季度回顾，优先保证已签约客户的稳定性，再开放新能力。欢迎在用户委员会提出场景投票。'),
    (16, '春节期间服务安排：技术支持保持值班', '2025-01-20', '官方新闻',
     '除夕至初六为轮班值守，紧急故障仍按 SLA 响应，常规需求初七起恢复处理。',
     '春节将至，感谢各位客户一年的信任。除夕至初六，技术支持改为轮班值守，P1/P2 故障仍按服务协议响应；需求咨询、培训预约等常规事项自初七起恢复。\n\n建议提前完成版本升级和备份演练。值班电话与邮箱保持不变，祝大家新春愉快。'),
    (17, '招聘启事：后端、前端与实施工程师', '2025-03-03', '官方新闻',
     '北京、杭州两地扩招，欢迎有企业软件或政务信息化经验的同学加入。',
     '随着交付规模扩大，公司在北京、杭州两地扩招后端、前端和实施工程师。我们看重把复杂需求拆成可上线增量的能力，也看重和客户一起把方案落地的耐心。\n\n简历请发送至 hr@example.com，邮件标题注明岗位和期望城市。通过初筛后会安排线上技术交流。'),
    (18, '数据中台 2.0 发布，统一企业数据资产目录', '2025-04-16', '产品动态',
     '新增血缘可视化和质量规则，帮助业务部门看清指标从哪来、能不能信。',
     '数据中台 2.0 已发布。此版本增加资产目录、血缘可视化和质量规则，业务人员可以按主题检索指标，并看到上游表、刷新时间和责任人。\n\n对已经使用智能办公的客户，中台可复用同一套组织权限。升级需评估现有数仓接口，实施周期通常为 4 到 8 周。'),
    (19, '亮相 2025 中国软博会，智能办公方案获创新奖', '2025-06-21', '行业资讯',
     '展会期间完成多场现场演示，并与三家区域集成商达成意向合作。',
     '瑞学软件参加 2025 中国国际软件博览会，智能办公解决方案获评创新产品。展台围绕“一个工作台看完待办、制度和经营数据”做了连续演示，接待了政务、制造和教育行业的参观团。\n\n会期还与三家区域集成商签署意向合作，后续将在本地招投标中联合出场。感谢到场交流的新老朋友。'),
    (20, '全国技术支持升级为 7×12 小时，新增远程巡检', '2025-08-08', '官方新闻',
     '工作日 8:00-20:00 受理故障，每月可预约一次远程巡检，提前发现证书和备份问题。',
     '自 8 月起，全国技术支持升级为每周七天、每天 12 小时（8:00-20:00）。标准版客户每月可预约一次远程巡检，重点检查证书过期、备份失败和磁盘水位。\n\n升级不额外收费。请管理员在门户中确认值班联系人，以免告警发到已离职账号。'),
]

# 留言模拟数据：(name, email, subject, content, created_at, status, reply, replied_at)
messages = [
    ("王经理", "wang@example.com", "想了解智能办公系统报价", "我们是一家约 200 人的制造企业，想了解智能办公的部署方式和报价区间。", "2025-08-12 10:20:00", "pending", None, None),
    ("李老师", "li@school.edu.cn", "教育行业是否有现成方案", "学校想做通知和审批，请问有没有教育行业的实施案例？", "2025-08-18 15:05:00", "replied", "有的，已有多所学校使用通知和审批模块。我们会把案例发给您，并安排一次远程演示。", "2025-08-18 17:40:00"),
    ("陈工", "chen@partner.com", "咨询生态合作", "我们是区域集成商，想了解伙伴认证和联合投标流程。", "2025-09-02 09:18:00", "pending", None, None),
    ("演示用户", "user@rxweb.com", "想预约一次产品演示", "我注册后想看看自己的留言和回复会出现在哪里。", "2025-09-10 11:20:00", "replied", "可以的。登录后打开“我的留言”即可查看本条记录和回复。", "2025-09-10 14:05:00"),
]

# 下载资源模拟数据
downloads = [
    (1, 'RxWeb前端框架V3.0.zip', '包含完整的框架代码、文档和示例。', '3.0.0', '25.8 MB', '2024-06-18'),
    (2, '智能办公系统用户手册.pdf', '详细介绍了系统的各项功能和使用方法。', '1.0.0', '5.2 MB', '2024-06-20'),
    (3, '产品介绍白皮书.pdf', '深入解读我们核心产品的技术架构与商业价值。', '2.1.0', '12.3 MB', '2024-05-30'),
    (4, 'API接口文档.md', '为开发者提供的详细接口说明和调用示例。', '1.5.2', '1.1 MB', '2024-06-22'),
    (5, '安全补丁SP2406.patch', '针对近期发现的安全漏洞的修复补丁。', '1.0.1', '876 KB', '2024-06-12'),
    (6, '公司Logo及VI设计规范.zip', '包含公司全套Logo矢量图和VI使用规范。', '2.0', '18.9 MB', '2024-04-10'),
]

# 默认写到项目根目录 company.db；Docker 可设置 RXWEB_DB 指向数据卷
_db_path = os.environ.get(
    "RXWEB_DB",
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "company.db")),
)
conn = sqlite3.connect(_db_path)
c = conn.cursor()

# 创建表
c.execute('''DROP TABLE IF EXISTS products''')
c.execute('''CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price TEXT,
    category TEXT,
    image TEXT,
    description TEXT
)''')
c.execute('''DROP TABLE IF EXISTS news''')
c.execute('''CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY,
    title TEXT,
    date TEXT,
    source TEXT,
    summary TEXT,
    content TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY,
    name TEXT,
    description TEXT,
    version TEXT,
    size TEXT,
    date TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    subject TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    reply TEXT,
    replied_at TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS admins (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
)''')
c.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    name TEXT,
    role TEXT NOT NULL DEFAULT 'user',
    reset_token TEXT,
    reset_expires TEXT,
    created_at TEXT
)''')
c.execute('''CREATE TABLE IF NOT EXISTS operation_logs (
    id INTEGER PRIMARY KEY,
    created_at TEXT NOT NULL,
    username TEXT,
    action TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    detail TEXT,
    result TEXT NOT NULL DEFAULT 'success',
    ip TEXT
)''')

# 清空表
c.execute('DELETE FROM products')
c.execute('DELETE FROM news')
c.execute('DELETE FROM downloads')
c.execute('DELETE FROM messages')
c.execute('DELETE FROM admins')
c.execute('DELETE FROM users')

# 插入数据
c.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', products)
c.executemany('INSERT INTO news VALUES (?, ?, ?, ?, ?, ?)', news)
c.executemany('INSERT INTO downloads VALUES (?, ?, ?, ?, ?, ?)', downloads)
c.executemany(
    'INSERT INTO messages (name, email, subject, content, created_at, status, reply, replied_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
    messages,
)
c.execute(
    'INSERT INTO admins (username, password_hash) VALUES (?, ?)',
    (os.environ.get("RXWEB_ADMIN_USER", "admin"), hash_password(os.environ.get("RXWEB_ADMIN_PASS", "rxweb123"))),
)
now = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
c.execute(
    'INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, ?, ?)',
    (os.environ.get("RXWEB_ADMIN_EMAIL", "admin@rxweb.com"), hash_password(os.environ.get("RXWEB_ADMIN_PASS", "rxweb123")), "管理员", "admin", now),
)
c.execute(
    'INSERT INTO users (email, password_hash, name, role, created_at) VALUES (?, ?, ?, ?, ?)',
    (os.environ.get("RXWEB_USER_EMAIL", "user@rxweb.com"), hash_password(os.environ.get("RXWEB_USER_PASS", "user123")), "演示用户", "user", now),
)

conn.commit()
conn.close()
print('种子数据已写入数据库。') 