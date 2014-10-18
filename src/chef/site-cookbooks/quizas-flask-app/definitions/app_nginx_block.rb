# define :app_nginx_block, :port => 4000, :hostname => nil do
define :app_nginx_block, :server_name => nil, :proxy_pass => nil do
    template "#{node['nginx']['dir']}/sites-available/#{params[:name]}" do
        source "my_nginx_site.erb"
        variables({
            "server_name" => params[:server_name],
            "proxy_pass" => params[:proxy_pass]
        })
    end
end
