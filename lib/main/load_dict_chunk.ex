defmodule DictLoader do
  def load_chunk(file_name) do
    "/Users/adnan/Qemotion/dsps_system/tmp_dict/#{file_name}"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> StringMatching.Sharder.dispatch_patterns
  end

  def load_chunk_remote(file_name) do
    "/home/ec2-user/opt/dsps_system/tmp_dict/#{file_name}"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> StringMatching.Sharder.dispatch_patterns
  end

  def load_chunk_2 do
    {:ok, pid_python} = :python.start(
      [{:python_path, '/Users/adnan/Qemotion/dsps_system/lib/master'},
       {:python, 'python3'}])
    # loop
    Enum.each(0..40, fn (y) ->
      patterns = "/Users/adnan/Qemotion/dsps_system/tmp_dict/22_char_words.csv"
      |> Path.expand(__DIR__)
      |> File.stream!
      |> CSV.decode!
      |> Enum.take(25000)
      |> Enum.map(fn x -> Enum.at(x,0) end)
      :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers', [patterns, [:a,:b,:c]])
      IO.puts y end)
    :python.stop(pid_python)
  end

  def shard_init do
    Master.Constructor.start(:ok, :ok)
    Cluster.Orchestrer.connect_nodes
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
    patterns = "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_9.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(1000000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Helpers.Hash.countby_length
    |> Cluster.Orchestrer.init_workers
  end

  def shard_init_2 do
    Master.Constructor.start(:ok, :ok)
    Cluster.Orchestrer.connect_nodes
    Cluster.Sharders.Dsupervisor.start_cluster_sharder("1")
    2..120 |> Enum.reduce(Map.new, fn x, acc -> Map.put(acc, x, 1000) end) |> Cluster.Orchestrer.init_workers
  end
  
  def shard_file(file_name) do
    patterns = "../../#{file_name}"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(1000000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> Enum.filter(fn x -> String.length(x) >= 2 end)
    |> Cluster.Sharder.dispatch_patterns("1")
  end

  def shard_data do
    Path.wildcard("tmp_data2/*.csv")
    |> Enum.each(fn x -> shard_file(x) end)
  end

  def multiple_match(heystack) do
    results = ParallelTask.new
      # Add some long running tasks eg. API calls
      |> ParallelTask.add(task_1: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_2: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_3: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_4: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_5: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_6: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_7: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.add(task_8: fn -> Client.EndPoint.match(heystack) end)
      |> ParallelTask.perform
  end
  
  
  """
  Node.Servers.get |> Enum.map(fn {_x, y} -> StringMatching.Metadata.get(MapSet.to_list(y) |> Enum.at(0)) end)
  Node.Servers.get |> Enum.reduce(0, fn {_x, y}, acc -> StringMatching.Metadata.get(MapSet.to_list(y) |> Enum.at(0)) |> (fn {_,x,_,_} -> x + acc end).() end)

Helpers.Benchmarkers.measure_runtime(fn -> 
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement")
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement") 
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement")
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement")
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement") 
  Client.EndPoint.match("je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassion vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraiment autant miséricordieusement sh5a5 matthieu et adnan je teste le bordel dans ce système casse couilles rapiecetez pas vraiment aussi consolidassions vraiment plus 93791bf8-792d-4589-99a7-4d0ba83fbc0fpas vraimentQSqsqS  autant miséricordieusement") end)
  """
  def load_chunk_3 do
    {:ok, pid_python} = :python.start(
      [{:python_path, '/Users/adnan/Qemotion/dsps_system/lib/master'},
       {:python, 'python3'}])
    :python.call(
      pid_python, :patterns_handler,
      :'Adnan.test',
      []) 
  end  
  
end


