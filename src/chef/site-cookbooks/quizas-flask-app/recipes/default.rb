#
# Cookbook Name:: quizas-flask-app
# Recipe:: default
#



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
%w{current
   current/html
   latest
   staticfiles.git
   staticfiles}.each do |dir|
    directory "/home/vagrant/flask-app/#{dir}" do
        owner "vagrant"
        group "vagrant"
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
    user "vagrant"
    cwd "/home/vagrant/flask-app/"
    code <<-EOH
    git init staticfiles.git --bare
    git clone staticfiles.git staticfiles
    EOH

    # Idempotent my arse
    not_if {Dir.exists?("/home/vagrant/flask-app/staticfiles/.git")}
end



# See http://docs.getchef.com/opscode_cookbooks_python.html
include_recipe "python"
# Use pip to install Flask.
python_pip "flask"



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

# Externalize conection info in a ruby hash
mysql_connection_info = {
  :host     => 'localhost',
  :username => 'root',
  :port     => node['mysql']['port'],
  :password => node['mysql']['server_root_password']
}

# Can create users
# # create a mysql user but grant no privileges
# mysql_database_user 'disenfranchised' do
#   connection mysql_connection_info
#   password 'super_secret'
#   action :create
# end
# 
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

mysql_database 'foo' do
  connection mysql_connection_info
  action :create
end

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

# Use Templates or files for our nginx conf files??

service 'nginx' do
    # http://docs.getchef.com/resource_service.html
    # 'reload' reloads conf
    action :reload
end

# Do we need a cookbook to do this?
# -- Now, if we want multiple blocks, I think
#    the best thing to do would be to have a
#    template an iterate over this.
# SEE
# https://supermarket.getchef.com/cookbooks/application_nginx
# http://docs.getchef.com/lwrp_application_nginx.html



# Ensure the webapp can be run??
# (Like, that there's a TMux session-stuff for it?).


