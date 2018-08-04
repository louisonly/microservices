package com.huawei.mdt.configration;

import java.io.IOException;
import java.util.Properties;

import javax.sql.DataSource;

import org.apache.commons.logging.Log;
import org.apache.commons.logging.LogFactory;
import org.apache.ibatis.plugin.Interceptor;
import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Primary;
import org.springframework.core.io.DefaultResourceLoader;
import org.springframework.core.io.Resource;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.jdbc.datasource.DataSourceTransactionManager;
import org.springframework.transaction.PlatformTransactionManager;
import org.springframework.transaction.annotation.EnableTransactionManagement;
import org.springframework.transaction.annotation.TransactionManagementConfigurer;

import com.github.pagehelper.PageInterceptor;
import com.huawei.mdt.interceptor.SqlPrintInterceptor;

@Configuration
@ConfigurationProperties
@EnableTransactionManagement
public class MybatisConfiguration implements TransactionManagementConfigurer {

	private static Log logger = LogFactory.getLog(MybatisConfiguration.class);

	@Value("${mybatis.type-aliases-package:com.huawei.mdt.entity}")
	private String typeAliasesPackage;

	@Value("${mybatis.mapper-locations:classpath:mybatis/mapper/*.xml}")
	private String mapperLocations;

	@Value("${mybatis.config-location:classpath:mybatis/mybatis-config.xml}")
	private String configLocation;
	
	@Value("${debug:false}")
	private String sqlDebug;

	@Autowired
	private DataSource dataSource;

	@Bean(name = "sqlSessionFactory")
	@Primary
	public SqlSessionFactory sqlSessionFactory() {
		try {
			SqlSessionFactoryBean sessionFactoryBean = new SqlSessionFactoryBean();
			sessionFactoryBean.setDataSource(dataSource);
			sessionFactoryBean.setTypeAliasesPackage(typeAliasesPackage);
			Resource[] resources = new PathMatchingResourcePatternResolver().getResources(mapperLocations);
			sessionFactoryBean.setMapperLocations(resources);
			sessionFactoryBean.setConfigLocation(new DefaultResourceLoader().getResource(configLocation));

			Interceptor[] plugins = null;
			if (sqlDebug.equalsIgnoreCase("true")) {
				plugins = new Interceptor[] {pageHelper(), sqlPrintInterceptor()};
			} else {
				plugins = new Interceptor[] {pageHelper()};
			}		
			
			sessionFactoryBean.setPlugins(plugins);

			return sessionFactoryBean.getObject();
		} catch (IOException e) {
			logger.error("mybatis resolver mapper*xml is error", e);
			return null;
		} catch (Exception e) {
			logger.error("mybatis sqlSessionFactoryBean create error", e);
			return null;
		}
	}
	
	@Bean
	public PlatformTransactionManager annotationDrivenTransactionManager() {
		return new DataSourceTransactionManager(dataSource);
	}

	@Bean
	public SqlPrintInterceptor sqlPrintInterceptor() {
		return new SqlPrintInterceptor();
	}

	@Bean
	public PageInterceptor pageHelper() {
		PageInterceptor pageHelper = new PageInterceptor();
		Properties p = new Properties();
		p.setProperty("helperDialect", "oracle");
		p.setProperty("offsetAsPageNum", "true");
		p.setProperty("rowBoundsWithCount", "true");
		p.setProperty("pageSizeZero", "true");
		p.setProperty("reasonable", "true");
		p.setProperty("returnPageInfo", "check");
		p.setProperty("supportMethodsArguments", "true");
		p.setProperty("params", "count=countSql");
		pageHelper.setProperties(p);
		return pageHelper;
	}
}
