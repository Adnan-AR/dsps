defmodule Main_remote do
  alias Cluster.Sharders.Dsupervisor, as: Dsupervisor
  def init do
    Master.Constructor.start(:whatever,:whatever)
    Cluster.Orchestrer.connect_nodes
    __MODULE__.create_sm_servers(50)
    __MODULE__.shard_dictionary(
     "/Users/adnan/Qemotion/dsps_system/tmp_data2")
  end

  # Create servers on a specific machine
  def test_remote do
    Master.Constructor.start(:whatever,:whatever)
    Cluster.Orchestrer.connect_nodes
    Cluster.Orchestrer.create_sm_servers(
      "worker1@ip-10-0-10-234.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker2@ip-10-0-10-130.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker3@ip-10-0-10-208.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker4@ip-10-0-10-24.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker5@ip-10-0-10-213.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker6@ip-10-0-10-188.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker7@ip-10-0-10-58.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker8@ip-10-0-10-152.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker9@ip-10-0-10-22.eu-west-3.compute.internal", 10)
    Cluster.Orchestrer.create_sm_servers(
      "worker10@ip-10-0-10-161.eu-west-3.compute.internal", 10)
  end
    
  # Create String Matching servers
  def create_sm_servers(how_many) do
    Application.fetch_env!(:dsps, :nodes)
    |> Map.fetch!(:workers)
    |> Helpers.Parallel.pmap_async(fn x ->
      Cluster.Orchestrer.create_sm_servers(x, how_many) end)
  end
  # Shard one file
  def shard_dictionary_chunk(path, sharder_name) do
    Helpers.FileExt.read_dictionary(path, 100)
    |> Cluster.Sharder.dispatch_patterns(sharder_name)
  end
  # Sharder for every csv file in the dictionary
  def shard_dictionary(path \\ "~/opt/dsps_system/tmp_data2/") do
    Helpers.FileExt.ls_r(path)
    |> Helpers.Parallel.pmap_async(fn x ->
      Dsupervisor.start_cluster_sharder(Path.basename(x)) end)
    Process.sleep(1000)
    Helpers.FileExt.ls_r(path)
    |> Enum.map(fn x ->
      Task.async(fn ->
	__MODULE__.shard_dictionary_chunk(x, Path.basename(x)) end)
    end)
  end
      
  def launch_match do
    data = __MODULE__.extand(
      [" need not caravanned need not caravanned  vines need "], 1000)
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
  
end

