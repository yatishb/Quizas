#
# Cookbook Name:: quizas-flask-app
# Recipe:: default
#

flaskapp_user = node["flask-app"]["user"]
flaskapp_dir  = node["flask-app"]["dir"]

# TODO: Customise app port; (in Flask app, in node, in this conf)
flaskapp_port = '5000'

flaskapp_db = "flaskapp"

# Ensure we have Python (and whatever else we need) installed
# `package` uses apt-get. You can check the following make sense
# on http://packages.ubuntu.com/

# From http://stackoverflow.com/questions/5339690/installing-multiple-packages-via-vagrant-chef
execute "update package index" do
  command "apt-get update"
  ignore_failure true
  action :nothing
end.run_action(:run)

%w(git ruby-dev).each do |pack|
    # Fuck chef_gem
    # This needs to be this syntax, so that it gets installed
    # at 'compile time'
    package(pack).run_action(:install)
end


# Folders for the Web app
# within the %w{}, list the folders we want
# within the `flask-app` folder.
#
# Assumptions/Expectations:
# * Static served in current/html/
#   * See below for assumptions about static src in repo.
# * Flask app served from current/py
%w{current
   current/html
   current/html/js
   current/html/css
   current/py
   latest
   staticfiles.git
   staticfiles}.each do |dir|
    directory "#{flaskapp_dir}/#{dir}" do
        owner flaskapp_user
        group flaskapp_user
        mode "0755"
        action :create

        # Genius, this doesn't use `owner` recursively
        # So.. cannot later create anything in
        # `flask-app` dir. :|
        recursive true
    end
end



# Ensure there is a bare git repo there
# (the `git` chef resource is for cloning existing
#  resources. Cloning an empty repo isn't its thing).
bash "setup staticfiles repos" do
    user flaskapp_user
    cwd flaskapp_dir
    code <<-EOH
    git init staticfiles.git --bare
    git clone staticfiles.git staticfiles
    EOH

    # Idempotent my arse
    not_if {Dir.exists?("#{flaskapp_dir}/staticfiles/.git")}
end



# See http://docs.getchef.com/opscode_cookbooks_python.html
include_recipe "python"

# Use pip to install Flask.
python_pip "flask"
python_pip "sqlalchemy"
python_pip "flask-sqlalchemy"



# Install + Configure Databases,
# Oracle MySQL

# See
# https://supermarket.getchef.com/cookbooks/mysql/versions/5.5.3

node.set['mysql']['server_root_password'] = 'yolo'
node.set['mysql']['port'] = '3308'
node.set['mysql']['data_dir'] = '/data'

include_recipe 'mysql::server'



# -- How can we, say, have different databases
#    setup for dev, staging, production?
#    * Use different EC2 Servers??
#      (This feels reasonably tidy, if you can easily
#       point to it).
#    * Create different DBs, have different copies
#      of flask web app, loading different keys.

# Setup Databases, Database Users

# See
# https://supermarket.getchef.com/cookbooks/database

include_recipe "database::mysql"

# Externalize conection info in a ruby hash
mysql_connection_info = {
  :host     => 'localhost',
  :username => 'root',
  :port     => Integer(node['mysql']['port']),
  :password => node['mysql']['server_root_password']
}

# Can create users
# # create a mysql user but grant no privileges
# mysql_database_user 'disenfranchised' do
#   connection mysql_connection_info
#   password 'super_secret'
#   action :create
# end

mysql_database flaskapp_db do
  connection mysql_connection_info
  action :create
end

# Database URIs
# (Easiest to directly give our Flask App a 
#  Database URI with username + password).
# See
# http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html#database-urls

# As a file, in Python can simply read all the contents of a file
# with
# `db_uri = open("/path/to/flask_db.uri", "r").read()
db_user = 'root'
db_passwd = node['mysql']['server_root_password']
file "#{flaskapp_dir}/flask_db.uri" do
    owner flaskapp_user
    group flaskapp_user
    mode "0755"
    content "mysql://#{db_user}:#{db_passwd}@localhost:#{node['mysql']['port']}/#{flaskapp_db}"
    action :create_if_missing
end

# # grant select,update,insert privileges to all tables in foo db from all hosts, requiring connections over SSL
# mysql_database_user 'foo_user' do
#   connection mysql_connection_info
#   password 'super_secret'
#   database_name 'foo'
#   host '%'
#   privileges [:select,:update,:insert]
#   require_ssl true
#   action :grant
# end

# We could pre-fill a database like the following:
# # Query a database
# mysql_database 'flush the privileges' do
#   connection mysql_connection_info
#   sql        'flush privileges'
#   action     :query
# end
#
# # Query a database from a sql script on disk
# mysql_database 'run script' do
#   connection mysql_connection_info
#   sql { ::File.open('/path/to/sql_script.sql').read }
#   action :query
# end



# Ensure Nginx is there,
# And configured for the site.

# See
# https://supermarket.getchef.com/cookbooks/nginx

include_recipe "nginx"

# See
# http://stackoverflow.com/questions/17133829/how-to-disable-default-nginx-site-when-using-chef-and-vagrant#17769713
# Seems there's an `nginx_site` lwrp we can use.

# Disable default site,
# Create and enable sites for other site(s)

# # Disable 'default' site
# nginx_site 'default' do
#   enable false
# end

# node['nginx']['dir'] is path to nginx conf dir

service 'nginx' do
    # http://docs.getchef.com/resource_service.html
    # 'reload' reloads conf
    action :reload
end

# For definition of app_nginx_block
# See ../definitions/app_nginx_block.rb
#
# For the template nginx conf used by the definition
# See ../templates/default/my_nginx_site.erb

# TODO: WebSockets

# Create /etc/nginx/sites-available/my-flaskapp-site
app_nginx_block "my-flaskapp-site" do
    server_name "www.quizas.me"
    proxy_pass "http://localhost:#{flaskapp_port}/"
    static_root "#{flaskapp_dir}/current/html"
end



# Ensure the webapp can be run??
# (Like, that there's a TMux session-stuff for it?).

# Files can be copied from the COOKBOOK/files/default/ dir
# using the `cookbook_file` resource.
# See
# http://docs.getchef.com/resource_cookbook_file.html

# Assumptions:
# * `static_serve_dir` MUST be the same as `static_root`
#   for  `app_nginx_block`.
# * `static_src_dirs` is a list of src folders (from repo,
#   pushed to APPDIR/staticfiles.git) to copy static files from.

template "#{flaskapp_dir}/staticfiles.git/hooks/post-receive" do
    owner flaskapp_user
    group flaskapp_user
    mode "0755"
    source "CopyStaticToProduction.sh.erb"
    variables({
        "app_dir" => flaskapp_dir,
        "static_serve_dir" => "#{flaskapp_dir}/current/html",
        "static_src_dirs" => %w{src/html src/html/js src/html/css}
    })
end
