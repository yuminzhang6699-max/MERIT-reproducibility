# MERIT 复现补充材料

本仓库整理已有公开实现，并补充版本固定、基准生成流程、元数据规范、完整评估提示词、统一测试集及难度定义和核验工具。

原始实现为 [ctacyk/MERIT](https://github.com/ctacyk/MERIT)，原始数据为 [ANTICH/LongTS-Industrial](https://huggingface.co/datasets/ANTICH/LongTS-Industrial)。保留原作者及TimeBlender版权和许可证，不把原实现归为本仓库新增原创。

请从[复现指南](reproducibility/README.md)开始。无需GPU即可下载固定版本、验证1716条时序和8412个QA，并从公开原始QA重新打包得到与已发布test逐字节相同的文件。

关键澄清：采样点数T=生成间隔数L+1；难度按L计算，保存的total_length为T；事件区间为零起点左闭右开[start,end)。当前发布版只有统一test，不采用旧版train/val/test划分脚本。

原项目文档保存在[UPSTREAM_README.zh-CN.md](UPSTREAM_README.zh-CN.md)。
