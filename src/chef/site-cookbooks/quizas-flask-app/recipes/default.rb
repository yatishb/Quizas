#
# Cookbook Name:: quizas-flask-app
# Recipe:: default
#

# Ensure we have Python (and whatever else we need) installed
# `package` uses apt-get. You can check the following make sense
# on http://packages.ubuntu.com/

# From http://stackoverflow.com/questions/5339690/installing-multiple-packages-via-vagrant-chef

# This takes ~20s if we don't skip it.
# So, cheapo way is to make a file after we have run this,
# check for that file (and don't run if it exists).
execute "update package index" do
  command "apt-get update"
  ignore_failure true
  action :nothing
  not_if { File.exists?("/root/packages_have_been_upgraded.txt") }
end.run_action(:run)

file "/root/packages_have_been_upgraded.txt" do
    content "Just so we don't have to run `apt-get update` everytime"
end

%w(git ruby-dev).each do |pack|
    # Fuck chef_gem
    # This needs to be this syntax, so that it gets installed
    # at 'compile time'
    # See, e.g.
    # https://www.getchef.com/blog/2013/09/04/demystifying-common-idioms-in-chef-recipes/

    # Quicker to :upgrade than :install
    package(pack).run_action(:upgrade)
end


# TODO: User. `flask-app` user which can run the app but isn't
#       in sudoers file.






# See http://docs.getchef.com/opscode_cookbooks_python.html
include_recipe "python"

# Could shave ~3 seconds by skipping this if
# pip stuff already installed. Tidier not to.

# Use pip to install Flask.
%w{flask sqlalchemy flask-sqlalchemy}.each do |pypac|
    python_pip pypac
end



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

# Disable 'default' site
nginx_site 'default' do
  enable false
end

# Ensure the webapp can be run??
# (Like, that there's a TMux session-stuff for it?).

# Files can be copied from the COOKBOOK/files/default/ dir
# using the `cookbook_file` resource.
# See
# http://docs.getchef.com/resource_cookbook_file.html

quizas_app "default"
