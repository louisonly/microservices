确保一致性
并发情况下 确保只有一个实例执行

@Repository
public class MongoDao {
	
	@Autowired
	private MSAuditLogConfig mongoDaoConfig;
	
	@Autowired
	private MSConfigClient configClient;

	private HashMap<String, MongoClient> hashMapClient = 
			new HashMap<String, MongoClient>();
	private HashMap<String, MongoCollection<BasicDBObject>> hashMapCollection = 
			new HashMap<String, MongoCollection<BasicDBObject>>();
	
	public void appendLog(String moduleName, String jsonDBObj) {
		
		BasicDBObject bson = (BasicDBObject)JSON.parse(jsonDBObj);					
		getCollection(moduleName).insertOne(bson);
	}

	protected MongoCollection<BasicDBObject> getCollection(String moduleName) {
		if(!hashMapCollection.containsKey(moduleName)) {
			MongoClientURI connectionString = new MongoClientURI(mongoDaoConfig.getConnectionUrl());
			MongoClient mongoClient = new MongoClient(connectionString);
			hashMapClient.put(moduleName, mongoClient);
			
			MongoDatabase mongoDatabase = hashMapClient.get(moduleName).getDatabase(mongoDaoConfig.getDatabaseName());
			//规范mongodb命名，mongodb集合名禁止使用任何`_`以外的特殊字符，建议小写
			String collectionName = moduleName.replace("-", "_").toLowerCase();
			//获取当前数据库下所有集合名字，据此判断当前数据库下该集合是否存在，如果不存在，则创建该集合；存在，直接返回该集合
			MongoIterable<String> collections = mongoDatabase.listCollectionNames();
			
			boolean flag = isExistCollection(collections, collectionName);
			if(flag != true) {				
				//获取服务配置信息
				System.out.println("===current collection size is 0====");
				//String configInfo1 = configClient.getConfigInfo("audit-log", "-", moduleName);
				String configInfo = configClient.getConfigInfo("audit-log", "-", moduleName);
				//获取用于记录日志的固定集合的大小，单位为MB
				long logSize = getLogSize(configInfo);
				//设置固定集合属性
				CreateCollectionOptions options = new CreateCollectionOptions();
				options.capped(true);
				options.sizeInBytes(1024 * 1024 * logSize);
				synchronized (mongoDatabase) {
					MongoIterable<String> collections2 = mongoDatabase.listCollectionNames();
					if(!isExistCollection(collections2, collectionName)) {
						System.out.println("Second panduan");
						mongoDatabase.createCollection(collectionName, options);
					}
					
				}									
			}
			System.out.println("!!!current collection size > 0!!!");
			MongoCollection<BasicDBObject> logsCollection = mongoDatabase.getCollection(collectionName,
					BasicDBObject.class);
			hashMapCollection.put(moduleName, logsCollection);		
		}
		
		return hashMapCollection.get(moduleName);
	}
	//解析配置中心服务器返回的配置信息，获取用于记录日志的固定集合大小
	public long getLogSize(String configInfo) {
		JSONObject jsonObject = JSONObject.parseObject(configInfo);
		JSONArray properties = jsonObject.getJSONArray("propertySources");
		String source = properties.getJSONObject(0).getString("source");
		JSONObject target = JSONObject.parseObject(source);
		String logsize = target.getString("logsize");
		return Long.parseLong(logsize);
	}
	//判断是否存在该集合
	public boolean isExistCollection(MongoIterable<String> collections, String collectionName) {
		boolean flag = false;
		for(String name : collections) {
			if(name.equals(collectionName)) {
				flag = true;
				break;
			}
		}		
		return flag;		
	}
	
	public void close(String moduleName) {
		if (hashMapClient.containsKey(moduleName)) {
			
			MongoClient mongoClient = hashMapClient.get(moduleName);
			mongoClient.close();
			
			hashMapClient.remove(moduleName);
			hashMapCollection.remove(moduleName);
		}
	}
	
	public void close() {
		
		for(String moduleName : hashMapClient.keySet()){			
			close(moduleName);
        }  
	}
}
