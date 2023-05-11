**本项目提供Web界面及API接口**


**项目结构**
- start.cmd 及 start.sh: 启动脚本
- main.py: 主程序
- pipeline/: 模型预测流水线
- model/: 模型文件
- file/: 上传文件存储目录
- source/: 白名单文件目录
- static/: 页面文件目录
- requements.txt: 依赖包列表


*注意*
- 本项目依赖于chrome与chromedriver，根目录提供了两者的安装包(如环境中已有chrome，请手动下载并安装对应版本的chromedriver):
  - ChromeSetup.exe
  - ChromeSetup.exe
- 首次运行时会从文件服务器下载模型文件，下载时间约5分钟，请耐心等待
- 请确保运行环境中具备6GM显存以上的GPU


**Web界面**
可使用单例预测或上传URL数据集进行预测，并提供可视化结果


**API接口**
提供了单例预测和批量预测接口，同时提供Swagger UI接口文档，可用于接口测试
在程序加载完成后，Swagger UI将自动运行于：localhost:8080/docs