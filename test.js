const pptxgen = require("pptxgenjs");

// 初始化演示文稿
let pres = new pptxgen();
pres.layout = 'LAYOUT_16x9';
pres.author = '医学科普团队';
pres.title = 'HPV病毒科普';

// 创建幻灯片
let slide = pres.addSlide();
slide.background = { color: "F5F0E6" }; // 哑光米白纸张背景

// 主标题
slide.addText("1.1 HPV病毒基本特性", {
  x: 1, y: 1, w: 5, h: 0.6,
  fontSize: 22, fontFace: "Source Han Sans SC", bold: true,
  color: "8A9A5B", align: "left"
});

// 副标题
slide.addText("200多种型别的人乳头瘤病毒，主要通过皮肤黏膜接触传播", {
  x: 1, y: 1.8, w: 5, h: 0.5,
  fontSize: 16, fontFace: "Source Han Sans SC",
  color: "333333", align: "left"
});

// 核心结论
slide.addText("HPV是一类具有高度型别特异性的无包膜DNA病毒，传播途径多元，感染多呈隐性或亚临床状态且可被免疫系统自发清除，特定人群与上皮部位为易感区域。", {
  x: 1, y: 2.8, w: 5, h: 1.2,
  fontSize: 16, fontFace: "Source Han Sans SC",
  color: "333333", align: "left", lineSpacing: 1.5
});

// 分点展开（富文本）
slide.addText([
  // 病毒分类
  { text: "病毒分类：200+型别，按致病性分 ", options: { breakLine: false } },
  { text: "低危/高危型", options: { color: "8A9A5B", breakLine: false } },
  { text: "，疾病风险差异显著", options: { breakLine: true } },
  // 传播途径
  { text: "传播途径：以皮肤黏膜直接/", options: { breakLine: false } },
  { text: "性接触传播", options: { color: "8A9A5B", breakLine: false } },
  { text: "为主，可通过母婴/间接接触传播", options: { breakLine: true } },
  // 结构机制
  { text: "结构机制：无包膜双链DNA病毒，依赖宿主表皮细胞分裂复制，无全身感染", options: { breakLine: true } },
  // 感染特点
  { text: "感染特点：多为隐性/亚临床感染，潜伏期数周至数月，多数可被免疫清除", options: { breakLine: true } },
  // 易感特征
  { text: "易感特征：青少年、性活跃人群易感，好发于宫颈、肛门等复层鳞状上皮部位", options: { breakLine: false } }
], {
  x: 1, y: 4.2, w: 5, h: 2,
  fontSize: 16, fontFace: "Source Han Sans SC",
  color: "333333", align: "left", lineSpacing: 1.5
});

// 底部备注
slide.addText("医学科普内容，仅供参考", {
  x: 1, y: 6.8, w: 8, h: 0.3,
  fontSize: 12, fontFace: "Source Han Sans SC",
  color: "D4CFC7", align: "left"
});

// 右侧配图（高调科学可视化图）
slide.addImage({
  path: "",
  x: 6.5, y: 1.5, w: 3, h: 4,
  sizing: { type: "contain" },
  altText: "HPV病毒粒子科学可视化图"
});

// 右侧配图（高调科学可视化图）
slide.addImage({
  path: "",
  x: 6.5, y: 1.5, w: 3, h: 4,
  sizing: { type: "contain" },
  altText: "HPV病毒粒子科学可视化图2"
});

// 右侧配图（高调科学可视化图）
slide.addImage({
  path: "",
  x: 6.5, y: 1.5, w: 3, h: 4,
  sizing: { type: "contain" },
  altText: "HPV病毒粒子科学可视化图3"
});
// 生成PPT文件
pres.writeFile({ fileName: "HPV病毒基本特性科普.pptx" });