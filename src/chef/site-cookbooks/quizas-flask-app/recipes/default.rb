#
# Cookbook Name:: quizas-flask-app
# Recipe:: default
#



# Ensure we have Python (and whatever else we need) installed
# `package` uses apt-get. You can check the following make sense
# on http://packages.ubuntu.com/

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
# MySQL with MariaDB

# SEE
# https://github.com/joerocklin/chef-mariadb

# Fuck. You *can't* include these recipes without
# ruby-dev being installed first.
# Even though we take care of *that*, it seems that
# this needs to have happened before reading this recipe.`

# Set any relevant settings for MariaDB here?


# Runs the recipe, right?
include_recipe "mariadb"

# To use the `database` cookbook
include_recipe "mariadb::ruby"

# Output passwords and such to some file,
# so that our Flask app can reference it.


# -- How can we, say, have different databases
#    setup for dev, staging, production?
#    * Use different EC2 Servers??
#      (This feels reasonably tidy, if you can easily
#       point to it).
#    * Create different DBs, have different copies
#      of flask web app, loading different keys.




# Ensure Nginx is there,
# And configured for the site.

include_recipe "nginx"

# Disable default site,
# Create and enable sites for other site(s)

# Do we need a cookbook to do this?
# -- Now, if we want multiple blocks, I think
#    the best thing to do would be to have a
#    template an iterate over this.
# SEE
# https://supermarket.getchef.com/cookbooks/application_nginx
# http://docs.getchef.com/lwrp_application_nginx.html


# Ensure the webapp can be run??
# (Like, that there's a TMux session-stuff for it?).
