defmodule Main_local do
  def test_local_start do
    Master.Constructor.start(:whatever,:whatever)
    Cluster.Orchestrer.connect_nodes
    Process.sleep(1000)
    Cluster.Orchestrer.init_workers(%{1=>1625790, 2=> 175741})
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
    Cluster.Sharder.dispatch_patterns(["ks","zb","be","kh","fn"], "1")
  end
  
  def read_dic1 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_1.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(5000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns("1")
  end
  def read_dic2 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_2.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(5000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Cluster.Sharder.dispatch_patterns("2")
  end
  def read_dic3 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_3.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(5000)
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
      ["  need not caravanned   need not caravanned  vines need not need not deaned ksess not all glided  bzez 2youra ayre bhal shaghleh"], 1)
    IO.inspect(length(data))
    Helpers.Parallel.pmap(
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

