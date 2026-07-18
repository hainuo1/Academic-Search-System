USE `AcademicSearchDB`;

-- 清空所有数据（按外键依赖顺序，可重复执行）
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE `BrowseHistory`;
TRUNCATE TABLE `SearchHistory`;
TRUNCATE TABLE `KeywordSearchCount`;
TRUNCATE TABLE `UserSearchCount`;
TRUNCATE TABLE `Favorites`;
TRUNCATE TABLE `Citation`;
TRUNCATE TABLE `DocumentKeyword`;
TRUNCATE TABLE `Keywords`;
TRUNCATE TABLE `Documents`;
TRUNCATE TABLE `Users`;
SET FOREIGN_KEY_CHECKS = 1;

-- ====== 1. 用户 ======
INSERT INTO `Users` (`UserName`,`Password`,`Email`,`Question1`,`Answer1Hash`,`Question2`,`Answer2Hash`) VALUES ('admin','scrypt:32768:8:1$JFGjzMinnDKGZbbL$537deda27121867bd7138d937fa72ac1df1a7de36ecf20f1173d96389509e29ef06424e1968a149ff1fd49d73727fd7294af41617d34ceb598e5d9cab19ffd8f','admin@example.com','你最喜欢的城市？','scrypt:32768:8:1$5D4kQMmxUSsyfnvq$7e2edc47de8228529711e1c40dcf7d7f31c2fa2843dcfcca0f4df81b705beaa3b644d12aac50899bf1b2b3123d3b26898887a2554d153bf69be8593b15def50a','你的小学名称？','scrypt:32768:8:1$I1vxxIbxtxyHrHs1$8e7ffe93d806563ed1567bb2d625c8bbe2bf4abc47218712d6a1ea23e7791df51a079bcc23f5ba7cf07e5e8a2a667b7d55eadb8abb0ca45e8e21d64bf40bf46b');
INSERT INTO `Users` (`UserName`,`Password`,`Email`,`Question1`,`Answer1Hash`,`Question2`,`Answer2Hash`) VALUES ('张三','scrypt:32768:8:1$kIMGQF4uzsZcJdOp$03fe6c872c4becc2e65e9397c8ed4cafb45c5081c949766dd5a2179c1e21ce61358b2aa853ecd1491016e153ddea69dd72eecfd7bd18e57f6f3d3b87ce8ddf8a','zhangsan@example.com','你的生日是？','scrypt:32768:8:1$0BgevidtBxFGNHCs$81121992859e61611143c65d6ebe93872b0f066ee3b3800de62e5e1a2943ff0cff92e41edc0886be1874d933cee8d78232ca055918dfebfc63b6d5b2adc8180c','你的宠物名字？','scrypt:32768:8:1$H5ZMqTdTudXTh2Oh$a4e3332be1e64944241534954dc4c2138a28ec170597916636f8514160fdbcc040c14f99a9be5b91d002bfd1dcaf987b30c21c72db5156d6fa0ae39fdc6a2741');
INSERT INTO `Users` (`UserName`,`Password`,`Email`,`Question1`,`Answer1Hash`,`Question2`,`Answer2Hash`) VALUES ('李四','scrypt:32768:8:1$zUUz4xGsw0gaRFPb$4596c699123d4f584003140f3cacb949ae3c669e2bf557d9e5e674f0763e990f1474ef47b41b0092979d15dc77c0c08dd49892ef982a202a75d9f7d9325c9289','lisi@example.com','你的身份证后四位？','scrypt:32768:8:1$XDt4Ed6Y3tazVdTQ$11004df642039fab7bc92ae1301fbd5c6919c88263398be85cde537d7d1bda942c522c6d2e12dd3ac5968986605cf8d301630866cf8fdb555f463773bf837c52','你喜欢吃什么？','scrypt:32768:8:1$uASLpD761Dg0dfpB$c6e9c9f208ff2b24b9ed3f45315b3094a2513b0f69971f6e3f21670119aaebaa67b8c8f3b075f5e57629a68d00684e4b879350eb00334ca02e1494c2e938c639');
INSERT INTO `Users` (`UserName`,`Password`,`Email`,`Question1`,`Answer1Hash`,`Question2`,`Answer2Hash`) VALUES ('王五','scrypt:32768:8:1$JsJdZBzE4gqtsRKU$87ae316232336cbe6514b11b28ea60c434a42563522d4d241e5d3badf9fb0758c13ac97270e782614accbaa07a10f972f490e5539073fee18c1c88a3880a167f','wangwu@example.com','你的母亲名字？','scrypt:32768:8:1$w4lR1bBMgXDp4Fte$a694a8a780067fcd225b06dfa40046f7c2bda7b13b80c902ddf6077714c81accf457d588801fade12460991e84a38a407a02445cca39ae8c637548eff6455f20','你的父亲名字？','scrypt:32768:8:1$8I4xeET69QzAgU2A$b54e6b0f7de08df2d94a54178609f5e0b6b25f035d69e52b01e0d9e68c8ce028715c2310c3c4773d57a03f7bd07c03e8542c8b5c7e78ca15d5997357781d403d');
INSERT INTO `Users` (`UserName`,`Password`,`Email`,`Question1`,`Answer1Hash`,`Question2`,`Answer2Hash`) VALUES ('testuser','scrypt:32768:8:1$bTUDILrERNPfDiVM$39f5575411a944cb0f8d434235cdd1d85c344ae528ba6fd6dfd8d48756da26690ec03d7c4c14630500a765410eebd8a1e6925c7300fa2d119a883a371742e963','test@example.com','你的大学名称？','scrypt:32768:8:1$n6ftswAvmQhpDW5Y$15160f82ddb04a321826ce217133c8e3670774a98e60dfb16a60e841e3ed12c646d9f936f45620700e70a252b0c26f0bbc9dd4dd202f171c8581c5cb6c31a91f','你的专业是什么？','scrypt:32768:8:1$64RYUXAjEdnX5QkW$88550ff50e1c8eb64f29e1793cea18ca7d20a0e75d0a4c99ce76a4b7fff4dc61f0f2b0f0ee7ba2a4b1a5f3e77ffeb0f9d00f8ed0415c678831b6395ce3fd1f45');

-- ====== 2. 文献 ======
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('基于深度学习的自然语言处理综述','陈小明','深度学习技术近年来在自然语言处理领域取得了突破性进展。本文对卷积神经网络、循环神经网络、Transformer等主流架构在文本分类、命名实体识别、机器翻译、情感分析等任务中的应用进行了全面综述。','2024-03-15','计算机科学','',1,'深度学习;自然语言处理;Transformer;神经网络;文本分类','深度学习技术近年来在自然语言处理领域取得了突破性进展。本文对卷积神经网络、循环神经网络、Transformer等主流架构在文本分类、命名实体识别、机器翻译、情感分析等任务中的应用进行了全面综述。',256,89);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('Machine Learning Approaches for Medical Image Analysis','Li Wei, Zhang Hua','Medical image analysis plays a critical role in modern clinical diagnosis. This paper reviews state-of-the-art machine learning and deep learning approaches for medical image segmentation, classification, and detection.','2024-01-20','医学','',2,'Medical Imaging;Deep Learning;CNN;Computer Vision;Diagnosis','Medical image analysis plays a critical role in modern clinical diagnosis. This paper reviews state-of-the-art machine learning and deep learning approaches for medical image segmentation, classification, and detection.',142,45);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('量子计算在密码学中的应用研究','王建国, 刘芳','量子计算的快速发展对传统密码学构成了重大挑战。Shor算法和Grover算法展示了量子计算机在破解RSA、ECC等公钥密码体系方面的潜力。本文系统梳理了后量子密码学的主要技术路线。','2024-05-10','计算机科学','',3,'量子计算;密码学;后量子密码;Shor算法;网络安全','量子计算的快速发展对传统密码学构成了重大挑战。Shor算法和Grover算法展示了量子计算机在破解RSA、ECC等公钥密码体系方面的潜力。本文系统梳理了后量子密码学的主要技术路线。',198,67);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('大数据环境下隐私保护技术研究','赵雪梅','随着大数据技术的广泛应用，数据隐私保护成为社会各界关注的焦点。本文深入分析了差分隐私、联邦学习、安全多方计算、同态加密等前沿隐私保护技术的原理和适用场景。','2024-02-28','计算机科学','',1,'大数据;隐私保护;差分隐私;联邦学习;数据安全','随着大数据技术的广泛应用，数据隐私保护成为社会各界关注的焦点。本文深入分析了差分隐私、联邦学习、安全多方计算、同态加密等前沿隐私保护技术的原理和适用场景。',173,52);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('A Survey of Graph Neural Networks','Yang Ming, Chen Fei','Graph Neural Networks have emerged as a powerful tool for learning on graph-structured data. This survey provides a comprehensive overview of GNN architectures including GCN, GAT, GraphSAGE.','2024-04-05','计算机科学','',2,'Graph Neural Networks;GNN;GCN;Deep Learning;Graph Representation','Graph Neural Networks have emerged as a powerful tool for learning on graph-structured data. This survey provides a comprehensive overview of GNN architectures including GCN, GAT, GraphSAGE.',221,78);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('气候变化的生态系统影响与适应性策略','林海涛, 陈思远','全球气候变化已对陆地和水生生态系统产生深远影响。本文基于过去20年的观测数据和模型预测，分析了气温升高、降水模式改变和极端天气事件对生物多样性的影响。','2023-12-01','环境科学','',4,'气候变化;生态系统;生物多样性;适应性策略;碳排放','全球气候变化已对陆地和水生生态系统产生深远影响。本文基于过去20年的观测数据和模型预测，分析了气温升高、降水模式改变和极端天气事件对生物多样性的影响。',88,21);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('强化学习在自动驾驶决策系统中的应用','张晓峰','自动驾驶技术的核心挑战之一是在复杂动态环境中做出安全高效的决策。本文探讨了深度强化学习在自动驾驶决策规划中的应用。','2024-06-18','计算机科学','',3,'强化学习;自动驾驶;决策系统;深度强化学习;CARLA','自动驾驶技术的核心挑战之一是在复杂动态环境中做出安全高效的决策。本文探讨了深度强化学习在自动驾驶决策规划中的应用。',134,38);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('新能源材料的设计与计算模拟','刘阳, 孙浩然','第一性原理计算和分子动力学模拟在新能源材料开发中发挥着越来越重要的作用。本文综述了密度泛函理论、机器学习势函数等方法在锂离子电池电极材料等领域的应用。','2024-03-28','材料科学','',4,'新能源材料;DFT;分子动力学;锂电池;钙钛矿','第一性原理计算和分子动力学模拟在新能源材料开发中发挥着越来越重要的作用。本文综述了密度泛函理论、机器学习势函数等方法在锂离子电池电极材料等领域的应用。',67,15);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('知识图谱构建与推理技术综述','陈小明, 王建国','知识图谱作为一种结构化的语义知识库，在智能搜索、问答系统、推荐系统等领域发挥着关键作用。本文系统梳理了知识图谱的构建流程，并对比分析了基于符号逻辑和基于表示学习的知识推理方法。','2024-04-22','计算机科学','',1,'知识图谱;知识推理;信息抽取;自然语言处理;表示学习','知识图谱作为一种结构化的语义知识库，在智能搜索、问答系统、推荐系统等领域发挥着关键作用。本文系统梳理了知识图谱的构建流程，并对比分析了基于符号逻辑和基于表示学习的知识推理方法。',180,56);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('脑机接口技术的发展现状与伦理思考','赵雪梅, 林海涛','脑机接口技术近年来取得了显著进展，从实验室逐渐走向临床应用。本文介绍了侵入式、半侵入式和非侵入式脑机接口技术的最新进展和伦理问题。','2024-05-30','交叉学科','',2,'脑机接口;神经科学;人工智能;伦理;Neuralink','脑机接口技术近年来取得了显著进展，从实验室逐渐走向临床应用。本文介绍了侵入式、半侵入式和非侵入式脑机接口技术的最新进展和伦理问题。',110,33);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('区块链技术在供应链金融中的应用','刘芳','供应链金融面临信用传递困难、信息不对称和操作效率低等痛点。区块链技术以其去中心化、不可篡改和可追溯的特性，为供应链金融提供了创新解决方案。','2024-01-15','经济学','',5,'区块链;供应链金融;智能合约;联盟链;金融科技','供应链金融面临信用传递困难、信息不对称和操作效率低等痛点。区块链技术以其去中心化、不可篡改和可追溯的特性，为供应链金融提供了创新解决方案。',75,18);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('深度学习在蛋白质结构预测中的突破','孙浩然, 张晓峰','AlphaFold2的问世标志着蛋白质结构预测领域的革命性突破。本文深入解析了AlphaFold2的Evoformer架构、结构模块和端到端训练策略。','2024-02-10','生物学','',3,'AlphaFold;蛋白质结构预测;深度学习;生物信息学;药物发现','AlphaFold2的问世标志着蛋白质结构预测领域的革命性突破。本文深入解析了AlphaFold2的Evoformer架构、结构模块和端到端训练策略。',156,48);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('教育数字化转型的理论框架与实施路径','陈思远','教育数字化转型是全球教育改革的重要趋势。本文构建了包含数字基础设施、数字素养、数字内容和数字治理四个维度的教育数字化理论框架。','2024-06-01','教育学','',4,'教育数字化;教育技术;智慧教育;在线学习;人工智能教育','教育数字化转型是全球教育改革的重要趋势。本文构建了包含数字基础设施、数字素养、数字内容和数字治理四个维度的教育数字化理论框架。',45,9);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('Sentiment Analysis Using Pre-trained Language Models','Yang Ming, Liu Yang','Pre-trained language models such as BERT, RoBERTa, and GPT have achieved state-of-the-art results in various sentiment analysis tasks. We propose a novel attention fusion mechanism.','2024-04-15','计算机科学','',2,'Sentiment Analysis;BERT;NLP;Attention Mechanism;Pre-trained Models','Pre-trained language models such as BERT, RoBERTa, and GPT have achieved state-of-the-art results in various sentiment analysis tasks. We propose a novel attention fusion mechanism.',189,62);
INSERT INTO `Documents` (`Title`,`Author`,`Abstract`,`PublishDate`,`Category`,`FilePath`,`UploadUserID`,`KeywordsText`,`FullText`,`ViewCount`,`DownloadCount`) VALUES ('城市交通拥堵的时空模式分析与预测','张晓峰, 刘阳','城市交通拥堵是困扰现代城市发展的全球性问题。本文基于大规模浮动车GPS轨迹数据，运用时空聚类分析、图神经网络和LSTM等方法对城市交通拥堵进行了系统建模。','2024-03-05','交通运输','',1,'交通拥堵;时空分析;GPS轨迹;图神经网络;深度学习','城市交通拥堵是困扰现代城市发展的全球性问题。本文基于大规模浮动车GPS轨迹数据，运用时空聚类分析、图神经网络和LSTM等方法对城市交通拥堵进行了系统建模。',102,28);

-- ====== 3. 关键词 ======
INSERT INTO `Keywords` (`KeywordName`) VALUES ('深度学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('自然语言处理');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Transformer');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('神经网络');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('文本分类');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Medical Imaging');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Deep Learning');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('CNN');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Computer Vision');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Diagnosis');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('量子计算');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('密码学');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('后量子密码');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Shor算法');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('网络安全');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('大数据');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('隐私保护');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('差分隐私');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('联邦学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('数据安全');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Graph Neural Networks');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('GNN');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('GCN');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Graph Representation');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('气候变化');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('生态系统');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('生物多样性');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('适应性策略');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('碳排放');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('强化学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('自动驾驶');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('决策系统');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('深度强化学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('CARLA');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('新能源材料');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('DFT');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('分子动力学');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('锂电池');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('钙钛矿');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('知识图谱');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('知识推理');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('信息抽取');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('表示学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('脑机接口');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('神经科学');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('人工智能');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('伦理');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Neuralink');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('区块链');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('供应链金融');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('智能合约');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('联盟链');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('金融科技');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('AlphaFold');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('蛋白质结构预测');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('生物信息学');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('药物发现');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('教育数字化');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('教育技术');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('智慧教育');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('在线学习');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('人工智能教育');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Sentiment Analysis');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('BERT');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('NLP');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Attention Mechanism');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('Pre-trained Models');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('交通拥堵');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('时空分析');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('GPS轨迹');
INSERT INTO `Keywords` (`KeywordName`) VALUES ('图神经网络');

-- ====== 4. 文献-关键词关联 ======
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 1, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '深度学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 1, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '自然语言处理';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 1, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Transformer';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 1, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '神经网络';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 1, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '文本分类';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 2, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Medical Imaging';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 2, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Deep Learning';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 2, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'CNN';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 2, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Computer Vision';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 2, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Diagnosis';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 3, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '量子计算';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 3, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '密码学';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 3, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '后量子密码';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 3, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Shor算法';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 3, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '网络安全';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 4, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '大数据';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 4, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '隐私保护';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 4, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '差分隐私';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 4, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '联邦学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 4, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '数据安全';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 5, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Graph Neural Networks';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 5, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'GNN';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 5, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'GCN';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 5, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Deep Learning';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 5, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Graph Representation';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 6, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '气候变化';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 6, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '生态系统';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 6, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '生物多样性';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 6, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '适应性策略';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 6, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '碳排放';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 7, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '强化学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 7, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '自动驾驶';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 7, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '决策系统';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 7, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '深度强化学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 7, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'CARLA';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 8, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '新能源材料';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 8, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'DFT';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 8, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '分子动力学';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 8, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '锂电池';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 8, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '钙钛矿';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 9, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '知识图谱';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 9, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '知识推理';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 9, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '信息抽取';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 9, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '自然语言处理';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 9, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '表示学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 10, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '脑机接口';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 10, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '神经科学';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 10, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '人工智能';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 10, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '伦理';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 10, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Neuralink';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 11, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '区块链';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 11, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '供应链金融';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 11, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '智能合约';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 11, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '联盟链';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 11, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '金融科技';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 12, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'AlphaFold';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 12, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '蛋白质结构预测';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 12, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '深度学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 12, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '生物信息学';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 12, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '药物发现';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 13, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '教育数字化';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 13, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '教育技术';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 13, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '智慧教育';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 13, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '在线学习';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 13, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '人工智能教育';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 14, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Sentiment Analysis';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 14, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'BERT';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 14, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'NLP';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 14, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Attention Mechanism';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 14, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'Pre-trained Models';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 15, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '交通拥堵';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 15, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '时空分析';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 15, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = 'GPS轨迹';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 15, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '图神经网络';
INSERT INTO `DocumentKeyword` (`DocumentID`,`KeywordID`,`TF_IDF`) SELECT 15, k.`KeywordID`, 1.0 FROM `Keywords` k WHERE k.`KeywordName` = '深度学习';

-- ====== 5. 引用关系 ======
INSERT INTO `Citation` (`SourceDocumentID`,`TargetDocumentID`) VALUES (1,9),(1,14),(5,2),(5,9),(7,15),(3,4),(8,12),(9,1),(14,1),(12,2),(10,6),(15,7),(4,11),(6,8);

-- ====== 6. 收藏 ======
INSERT INTO `Favorites` (`UserID`,`DocumentID`) VALUES (1,1),(1,9),(1,2),(1,5),(2,5),(2,14),(2,1),(3,7),(3,12),(3,4),(4,6),(4,13),(5,1),(5,11);

-- ====== 7. 检索历史 ======
INSERT INTO `SearchHistory` (`UserID`,`SearchKeyword`,`SearchTime`) VALUES
(1,'深度学习',NOW()-INTERVAL 1 DAY),(1,'自然语言处理',NOW()-INTERVAL 2 DAY),(1,'知识图谱',NOW()-INTERVAL 3 DAY),(1,'脑机接口',NOW()-INTERVAL 4 DAY),(1,'自动驾驶',NOW()-INTERVAL 5 DAY),
(2,'Graph Neural Networks',NOW()-INTERVAL 1 DAY),(2,'Medical Image',NOW()-INTERVAL 2 DAY),(2,'Sentiment Analysis',NOW()-INTERVAL 3 DAY),(2,'NLP',NOW()-INTERVAL 4 DAY),(2,'深度学习',NOW()-INTERVAL 5 DAY),
(3,'强化学习',NOW()-INTERVAL 1 DAY),(3,'量子计算',NOW()-INTERVAL 2 DAY),(3,'蛋白质结构',NOW()-INTERVAL 3 DAY),
(4,'气候变化',NOW()-INTERVAL 2 DAY),(4,'教育数字化',NOW()-INTERVAL 3 DAY),(4,'新能源材料',NOW()-INTERVAL 4 DAY),
(5,'区块链',NOW()-INTERVAL 1 DAY),(5,'金融科技',NOW()-INTERVAL 2 DAY);

-- ====== 8. 浏览历史 ======
INSERT INTO `BrowseHistory` (`UserID`,`DocumentID`,`ViewTime`) VALUES
(1,1,NOW()-INTERVAL 1 HOUR),(1,9,NOW()-INTERVAL 3 HOUR),(1,3,NOW()-INTERVAL 5 HOUR),(1,4,NOW()-INTERVAL 8 HOUR),(1,5,NOW()-INTERVAL 12 HOUR),
(2,5,NOW()-INTERVAL 2 HOUR),(2,14,NOW()-INTERVAL 4 HOUR),(2,2,NOW()-INTERVAL 10 HOUR),(2,1,NOW()-INTERVAL 24 HOUR),
(3,7,NOW()-INTERVAL 3 HOUR),(3,12,NOW()-INTERVAL 7 HOUR),(3,3,NOW()-INTERVAL 15 HOUR),(3,1,NOW()-INTERVAL 48 HOUR),
(4,6,NOW()-INTERVAL 6 HOUR),(4,13,NOW()-INTERVAL 10 HOUR),(4,1,NOW()-INTERVAL 24 HOUR),
(5,11,NOW()-INTERVAL 2 HOUR),(5,1,NOW()-INTERVAL 18 HOUR);

-- ====== 9. 用户搜索统计 ======
INSERT INTO `UserSearchCount` (`UserID`,`SearchCount`) VALUES (1,45),(2,32),(3,28),(4,19),(5,8);

-- ====== 10. 关键词搜索统计 ======
INSERT INTO `KeywordSearchCount` (`Keyword`,`SearchCount`) VALUES ('深度学习',87),('自然语言处理',65),('知识图谱',42),('量子计算',33),('强化学习',29),('Graph Neural Networks',25),('区块链',22),('气候变化',18),('Medical Imaging',16),('蛋白质结构',15);