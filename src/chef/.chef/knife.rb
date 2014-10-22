cookbook_path    ["cookbooks", "site-cookbooks"]
node_path        "nodes"
role_path        "roles"
environment_path "environments"
data_bag_path    "data_bags"

knife[:bootstrap_version] = '11'

# Let's use the same .pem as AWS gave us
# (for simplicity).
# Gotta know where this is, so.. look either at
# ENV[CS3216_ASSG4_CLIENT_KEY]
# or
# ./client_key.pem

if ENV.has_key?("CS3216_ASSG4_CLIENT_KEY")
    encrypted_data_bag_secret = ENV["CS3216_ASSG4_CLIENT_KEY"]
    puts "Using client key #{encrypted_data_bag_secret}"
elsif File.exists?(".chef/client_key.pem") || File.symlink?(".chef/client_key.pem")
    # in .chef/ directory
    encrypted_data_bag_secret = ".chef/client_key.pem"
    puts "Using client key #{encrypted_data_bag_secret}"
else
    puts <<-EOH
********************************************************************************
You need to specify either
* Environment variable CS3216_ASSG4_CLIENT_KEY
OR
* Link /src/chef/.chef/client_key.pem to cs3216final.pem
So that Chef can use encrypted Data Bags for passwords.
********************************************************************************
EOH
end

knife[:berkshelf_path] = "cookbooks"
