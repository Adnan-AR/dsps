defmodule StringMatching.SharderTest do
  use ExUnit.Case, async: false
  ExUnit.configure seed: 0
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Sharder, as: Sharder
  alias StringMatching.Metadata, as: Agent
  alias  StringMatching.Dsupervisor, as: DSupervisor
  doctest StringMatching.Sharder

  describe "count_patterns_bylength/2" do
    test "Get total words count by length in the node" do
      patterns = ["test1", "test2", "test3",
		  "test12", "test12", "test32",
		  "test124"]
      :timer.sleep(1000)
      # Expected results
      count_5 = 3
      count_6 = 2
      count_7 = 1
      count_8 = 0
      # Start the constructor
      Workers.Constructor.start(:ok, :ok)
      # start all workers with there agents
      DSupervisor.start_string_matching(:workerA, 5)
      DSupervisor.start_string_matching(:workerB, 6)
      DSupervisor.start_string_matching(:workerC, 7)
      DSupervisor.start_string_matching(:workerD, 8)
      # Dispatch words
      Sharder.dispatch_patterns(patterns)
      # Sleep till the sharding is done
      # Assert
      assert (
 	count_5 == Sharder.count_patterns_bylength(DSupervisor, 5)
	&& count_6 == Sharder.count_patterns_bylength(DSupervisor, 6)
	&& count_7 == Sharder.count_patterns_bylength(DSupervisor, 7)
	&& count_8 == Sharder.count_patterns_bylength(DSupervisor, 8))
      # Kill all process
      kill_all
    end
  end
  
  describe "local_dispatch/2" do
    test "dispatch patterns to a specific String Matching server and 
    test their states and metadata agents" do
      :timer.sleep(1000)
      # Start the constructor
      Workers.Constructor.start(:ok, :ok)
      # workers
      updated_worker_pos = 2
      workers = [:worker31, :worker32, :worker33]
      length = 5
      patterns = ["test1", "test2", "test3", "test4"]
      # Expected worker's states
      empty_worker_state = %Needles{
	length: length, patterns: MapSet.new}
      updated_worker_state = %Needles{
	length: length, patterns: MapSet.new(patterns)}
      # Expected String Matching Meta agent's states
      updated_agent = {
	MapSet.new(["test1","test2","test3","test4"]), 4, "test4", 5}
      empty_agent = {MapSet.new, 0, nil, 5}
      # start all workers
      pids = Enum.map(workers, fn x -> Worker.start_link(x, length) end)
      # start agents also (the Dsupervisor initiates that in production)
      agent_res = Enum.map(workers, fn x ->
	Agent.start_link(x, {MapSet.new, length}) end)
      IO.inspect(agent_res)
      IO.inspect(Enum.at(workers, updated_worker_pos)|> Agent.get)
      # add patterns to the third worker
      updated_worker = Enum.at(workers, updated_worker_pos)
      Sharder.dispatch_patterns(patterns, updated_worker)
      # Sleep till the sharding is done
      :timer.sleep(1000)
      # Print the state of each worker
      res = pids |> Enum.map(fn {:ok, p} -> :sys.get_state(p) end)
      # Print agent's states
      IO.inspect(Enum.at(workers, updated_worker_pos)|> Agent.get)
      IO.inspect(Enum.at(workers, updated_worker_pos-1)|> Agent.get)
      # Assert
      assert (
 	updated_worker_state == Enum.at(res, updated_worker_pos)
	&& updated_agent == Enum.at(workers, updated_worker_pos)|>Agent.get
	&& empty_worker_state == Enum.at(res, updated_worker_pos-1)
	&& empty_agent == Enum.at(workers, updated_worker_pos-1)|>Agent.get
      )
      # Kill all process
      kill_all
    end
  end

  
  describe "local_dispatch/2 one pattern sharding" do
    test "dispatch one pattern in a node, we add 5 patterns to three 
          workers then we add dispatch one pattern to the node via
          the sharder, this pattern should go the fourth worker" do
      :timer.sleep(1000)
      # Start the constructor
      Workers.Constructor.start(:ok, :ok)
      # Workers
      workers = [:worker21, :worker22, :worker23, :worker24]
      length = 5
      # Start workers and agents
      workers
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, length) end)
      IO.inspect(Helpers.ProcessesGetter.get_agents(DSupervisor))
      # Expected worker's states
      empty_worker_state = %Needles{
	length: length, patterns: MapSet.new}
      updated_worker_state_1 = %Needles{
	length: length, patterns: MapSet.new(["test1", "test2"])}
      updated_worker_state_2 = %Needles{
	length: length, patterns: MapSet.new(["test3", "test4"])}
      updated_worker_state_3 = %Needles{
	length: length, patterns: MapSet.new(["test5"])}
      updated_worker_state_4 = %Needles{
	length: length, patterns: MapSet.new(["test6"])}
      # Expected String Matching Meta agent's states
      updated_agent_1 = {MapSet.new(["test1","test2"]), 2, "test2", 5}
      updated_agent_2 = {MapSet.new(["test3","test4"]), 2, "test4", 5}
      updated_agent_3 = {MapSet.new(["test5"]), 1, "test5", 5}
      updated_agent_4 = {MapSet.new(["test6"]), 1, "test6", 5}
      empty_agent = {MapSet.new, 0, nil, 5}
      # add patterns to the third worker
      Sharder.dispatch_patterns(["test1", "test2"], :worker21)
      Sharder.dispatch_patterns(["test3", "test4"], :worker22)
      Sharder.dispatch_patterns("test5", :worker23)
      # This one should go to the fourth worker
      Sharder.dispatch_patterns("test6")
      # Sleep till the sharding is done
      :timer.sleep(1000)
      # Get the state of the fourth worker :worker4
      [{p,_}] = Registry.lookup(StringMatching.Servers.Registry, :worker24)
      IO.inspect(Agent.get(:worker24))
      :timer.sleep(1000)
      # Assert (3 is the position of the foiurth worker in the list)
      assert (
	updated_worker_state_4 == :sys.get_state(p)
	&& updated_agent_4 == Agent.get(:worker24))
      # Kill all process
      kill_all
    end
  end


  describe "local_dispatch/1 full list of patterns (empty workers)" do
    test "dispatch a full list of patterns to the whole node" do
      # Set patterns
      patterns = ["test1","test2","test3","test4",
		  "test5","test6","test7","test8",
		  "test9","tesy1","tesy2","tesy3",
		  "a","b","c","d","e","f","g","h",
		  "ke1","ke2","ke3","ke4","ke5"]
      # Start the constructor
      Workers.Constructor.start(:ok, :ok)
      # 4 wokers length 5
      workers_l5 = [:worker11, :worker12, :worker13, :worker14]
      l5 = 5
      # 3 workers length 3
      workers_l3 = [:worker15, :worker16, :worker17]
      l3 = 3
      # 2 workers length 1
      workers_l1 = [:worker18, :worker19, :worker110]
      l1 = 1
      # Start workers and agents
      workers_l5
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l5) end)
      workers_l3
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l3) end)
      workers_l1
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l1) end)     
      # Expected worker's states
      updated_worker_state_5 = %Needles{
	length: l5, patterns: MapSet.new(["test1", "test2","test3"])}
      updated_worker_state_3 = %Needles{
	length: l3, patterns: MapSet.new(["ke5"])}
      updated_worker_state_1 = %Needles{
	length: l1, patterns: MapSet.new(["g", "h"])}
      # Expected String Matching Meta agent's states
      updated_agent_5 = {MapSet.new(
			    ["test1", "test2", "test3"]), 3, "test3", 5}
      updated_agent_3 = {MapSet.new(["ke5"]), 1, "ke5", 3}
      updated_agent_1 = {MapSet.new(["g","h"]), 2, "h", 1}
      # add patterns to the third worker
      Sharder.dispatch_patterns(patterns)
      :timer.sleep(1000)
      # Get the state of some workers
      [{p5_1,_}] = Registry.lookup(
	StringMatching.Servers.Registry, :worker11)
      [{p3_3,_}] = Registry.lookup(
	StringMatching.Servers.Registry, :worker17)
      [{p3_2,_}] = Registry.lookup(
	StringMatching.Servers.Registry, :worker16)
      [{p3_1,_}] = Registry.lookup(
	StringMatching.Servers.Registry, :worker15)
      [{p1_3,_}] = Registry.lookup(
	StringMatching.Servers.Registry, :worker110)
      IO.inspect(:sys.get_state(p5_1))
      IO.inspect(:sys.get_state(p3_1))
      IO.inspect(:sys.get_state(p1_3))
      :timer.sleep(1000)
      # Assert (3 is the position of the foiurth worker in the list)
      assert (
	updated_worker_state_5 == :sys.get_state(p5_1)
	&& updated_agent_5 == Agent.get(:worker11) &&
      updated_worker_state_3 == :sys.get_state(p3_3)
	&& updated_agent_3 == Agent.get(:worker17) &&
      updated_worker_state_1 == :sys.get_state(p1_3)
	&& updated_agent_1 == Agent.get(:worker110))

      # Kill all active process
      kill_all
    end
  end

  describe "is_there/1 single pattern" do
    test "Words exists in the node?" do
      # Set patterns
      patterns = ["test1","test2","test3","test4",
       "test5","test6","test7","test8",
       "test9","tesy1","tesy2","tesy3",
       "a","b","c","d","e","f","g","h",
       "ke1","ke2","ke3","ke4","ke5"]
      # 4 wokers length 5
      workers_l5 = [:w11, :w12, :w13, :w14]
      l5 = 5
      # 3 workers length 3
      workers_l3 = [:w15, :w16, :w17]
      l3 = 3
      # 2 workers length 1
      workers_l1 = [:w18, :w19, :w110]
      l1 = 1
      Workers.Constructor.start(:ok,:ok)
      # Start workers and agents
      workers_l5
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l5) end)
      workers_l3
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l3) end)
      workers_l1
      |> Enum.each(fn x -> DSupervisor.start_string_matching(x, l1) end)     
      # add patterns to the third worker
      Sharder.dispatch_patterns(patterns)
      :timer.sleep(1000)
      # Assert
      assert (
	Sharder.is_there("test1") == true
	&&  Sharder.is_there("tesk1") == false
        &&  Sharder.is_there("f") == true
	&&  Sharder.is_there("y") == false
      )
      # Kill all active process
      kill_all
    end
  end

  # Kill the main Static and Dynamic supervisor with their children
  defp kill_all do
    # Kill Dynamic Supervisor's children
    DynamicSupervisor.which_children(DSupervisor)
    |> Enum.each(fn {_, pid, _, _} ->
      DynamicSupervisor.terminate_child(DSupervisor, pid) end)

    # Kill Static Supervisor's children 
    Supervisor.which_children(Workers.Constructor)
    |> Enum.each(fn {_, pid ,_ , _} ->
      Supervisor.terminate_child(Workers.Constructor, pid) end)

    # Kill the static supervisor
    # Supervisor.stop(Workers.Constructor)
    end
end
