#!/usr/bin/python
import simplejson
import os 
import sys 

tables = ["api_users", "area_config", "area_keys", "area_member_status", "audit_agents", "developer_classes", "email_template_sets", "email_templates", "members_apps", "method_overrides", "migration_log", "oauth2_access_tokens", "oauth2_authz_codes", "oauth_key_settings", "package_keys", "packages", "plan_endpoints", "plan_filters", "plan_methods", "plans", "response_filter_formats", "service_classes", "service_definition_endpoints", "service_definition_methods", "service_definition_responses", "service_mapi", "service_provider"] 

def truncate_table(tableName):
 	mysqlCommand = "mysql -u root -p'A@I+W=V1uPrkJmXQsTO0IFrp' -e 'truncate table " +  tableName + ";' onprem" 
 	print mysqlCommand 
 	os.system(mysqlCommand) 

def resetKeys(key, secret): 
	conf_file_path = '/etc/mashery-proxy-config.json' 
	conf = simplejson.load(open(conf_file_path, 'r')) 
	if conf.has_key('com.mashery.proxy.onpremloader'): 
		section = conf['com.mashery.proxy.onpremloader'] 
	if (section.has_key('apiKey') and section.has_key('apiSecret') and section.has_key('updatesEndpoint')): 
		section['apiKey'] = key 
		section['apiSecret'] = secret 
		x = simplejson.dump(conf, open(conf_file_path, 'w'), indent=4) 

for table in tables: 
	truncate_table(table) 

resetKeys(sys.argv[1], sys.argv[2])
os.system("/etc/init.d/javaproxy restart")