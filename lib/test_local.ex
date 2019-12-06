defmodule Main_local do
  def test_local_start do
    Master.Constructor.start(:whatever,:whatever)
    Cluster.Orchestrer.connect_nodes
    Cluster.Orchestrer.create_sm_servers(
      "node2@adnans-macbook-pro.home", 100)
    Cluster.Orchestrer.create_sm_servers(
      "node3@adnans-macbook-pro.home", 100)
    Cluster.Orchestrer.create_sm_servers(
      "node4@adnans-macbook-pro.home", 100)
    Cluster.Orchestrer.create_sm_servers(
      "node6@adnans-macbook-pro.home", 100)
    Process.sleep(1000)
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("2")
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("3")
  end
  
  def read_dic1 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data/new_aaedited.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(10000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns("1")
  end
  def read_dic2 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data/new_abedited.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(10000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns("2")
  end
  def read_dic3 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data/new_acedited.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(10000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns("3")
  end

  def launch do
    IO.puts("Launch the first")
    Task.async(fn -> __MODULE__.read_dic1 end)
    IO.puts("Launch the second")
    Task.async(fn -> __MODULE__.read_dic2 end)
    IO.puts("Launch the third")
    Task.async(fn -> __MODULE__.read_dic3 end)
  end

  def launch_match do
    data = __MODULE__.extand(
      ["  need not caravanned   need not caravanned  vines need not need not deaned ksess bzez 2youra ayre bhal shaghleh akalet khara wala abta2 men hek khara system b zabre"], 1000)
    IO.inspect(length(data))
    __MODULE__.pmap(
      data, fn x->Client.EndPoint.match(x) end) 
  end

  def extand(collection, i) when i==0 do
    collection
  end
  def extand(collection, i) do
    __MODULE__.extand(collection ++ [Enum.at(collection, 0)], i-1)
  end
  


  
  def read_dic_remote do
    "~/opt/dsps_system/tmp_data/new_as"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns
  end
 
end

