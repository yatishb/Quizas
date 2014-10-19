define :app_nginx_block, :server_name => nil, :proxy_pass => nil, :static_root => nil do
    template "#{node['nginx']['dir']}/sites-available/#{params[:name]}" do
        source "my_nginx_site.erb"
        variables({
            "server_name" => params[:server_name],
            "proxy_pass" => params[:proxy_pass],
            "static_root" => params[:static_root]
        })
    end
end
