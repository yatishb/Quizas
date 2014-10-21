define :quizas_app do
    # role = "dev", "test", "production", etc.
    role = params[:name]

    # Use attributes (e.g. defined in the Node)

    roleAttrHash = node["flask-app"][role] || {}
    flaskAppHash = node["flask-app"] || {}

    lookup = lambda {|k| roleAttrHash[k] || flaskAppHash[k] }

    flaskapp_user = lookup.call "user"
    flaskapp_dir  = lookup.call "dir"

    # TODO: Default attribute
    flaskapp_port = lookup.call "port"

    flaskapp_db = lookup.call "database_name"


    # TODO: FOREACH (stage, production)
    db_user = 'root'
    db_passwd = node['mysql']['server_root_password']

    nginx_sitename         = lookup.call "nginx_sitename"
    nginx_site_server_name = lookup.call "nginx_site_server_name"
    nginx_site_proxy_pass  = lookup.call "nginx_site_proxy_pass"
    nginx_site_static_root = lookup.call "nginx_site_static_root"



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


    # Externalize conection info in a ruby hash
    # TODO: It's Bad (tm) that this is the root MySQL acct.
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

    file "#{flaskapp_dir}/flask_db.uri" do
        owner flaskapp_user
        group flaskapp_user
        mode "0755"
        content "mysql://#{db_user}:#{db_passwd}@localhost:#{node['mysql']['port']}/#{flaskapp_db}"
        action :create_if_missing
    end



    # For definition of app_nginx_block
    # See ../definitions/app_nginx_block.rb
    #
    # For the template nginx conf used by the definition
    # See ../templates/default/my_nginx_site.erb

    # TODO: WebSockets

    # Create /etc/nginx/sites-available/my-flaskapp-site

    app_nginx_block nginx_sitename do
        server_name nginx_site_server_name
        proxy_pass  nginx_site_proxy_pass
        static_root nginx_site_static_root
    end

    nginx_site nginx_sitename do
      enable true
    end

    service 'nginx' do
        # http://docs.getchef.com/resource_service.html
        # 'reload' reloads conf
        action :reload
    end



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



    template "#{flaskapp_dir}/UpdateFlask.sh" do
        owner flaskapp_user
        group flaskapp_user
        mode "0755"
        source "UpdateFlask.sh.erb"
        variables({
            "app_dir" => flaskapp_dir
        })
    end
end
