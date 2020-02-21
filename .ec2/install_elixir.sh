#!/bin/bash

# Install some packages
yum install gcc gcc-c++ make libxslt fop ncurses-devel \
    openssl-devel *openjdk-devel unixODBC unixODBC-devel \
    autoconf automake git
# Clone asdf (package manager) from git repos
git clone https://github.com/asdf-vm/asdf.git ~/.asdf --branch v0.7.5

# Add asdf to PATH
export PATH="${PATH}:~/.asdf/bin/"
export PATH="${PATH}:~/.asdf/shims/"
mkdir ~/opt/dsps_system

# Add Erlang and Elixir as asdf plugins
asdf plugin-add erlang
asdf plugin-add elixir
# Install
asdf install elixir 1.9.1
asdf install erlang 22.1
asdf local elixir 1.9.1
asdf local erlang 22.1

#==================SCP project src to aws instances===================
ips=(
    ec2-user@ec2-35-180-197-193.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-35-180-231-19.eu-west-3.compute.amazonaws.com
    ec2-user@ec2-15-188-89-46.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-35-180-251-164.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-15-188-185-214.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-35-180-45-21.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-35-180-228-79.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-15-188-33-252.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-52-47-78-5.eu-west-3.compute.amazonaws.com
    ec2-user@ec2-52-47-82-122.eu-west-3.compute.amazonaws.com
    ec2-user@ec2-15-188-193-143.eu-west-3.compute.amazonaws.com
    #ec2-user@ec2-35-180-83-35.eu-west-3.compute.amazonaws.com
)
for ip in "${ips[@]}"; do
    sudo scp -i /Users/adnan/Qemotion/keys/dsps-key.pem -r\
	 dsps_system/ $ip:~/opt/dsps_system
done
#=====================================================================
iex --name master@ip-10-0-10-138.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name client@ip-10-0-10-85.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker1@ip-10-0-10-234.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker2@ip-10-0-10-130.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker3@ip-10-0-10-208.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker4@ip-10-0-10-24.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker5@ip-10-0-10-213.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker6@ip-10-0-10-188.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker7@ip-10-0-10-58.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker8@ip-10-0-10-152.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker9@ip-10-0-10-22.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix

iex --name worker10@ip-10-0-10-161.eu-west-3.compute.internal\
    --cookie test \
    --erl '-kernel inet_dist_listen_min 9100' \
    --erl '-kernel inet_dist_listen_max 9155' \
    -S mix
#=============================================================
