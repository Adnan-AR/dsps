defmodule BuildSharding do

  alias StringMatching.Dsupervisor, as: Ds
  
  def create_shards do
    # workers
    workers_5 = [:worker1, :worker2, :worker3, :worker4, :worker5]
    workers_3 = [:worker6, :worker7, :worker8]
    # 4 workers with the length 5
    Enum.take(workers_5, 4)
    |> Enum.each(fn x -> Ds.start_string_matching(x, 5) end)
    # 3 workers with the length 3 
    workers_3
    |> Enum.each(fn x -> Ds.start_string_matching(x, 3) end)
    # one worker with length of 1
    Enum.at(workers_5, -1)
    |> Ds.start_string_matching(1)

    StringMatching.Sharder.dispatch_patterns(
      ["test1","test2"], :worker1)
    StringMatching.Sharder.dispatch_patterns(
      ["test6","test5", "test3", "test4"], :worker2)
    StringMatching.Sharder.dispatch_patterns(
      ["tesb1","tesb2","tesb3"], :worker3)
    StringMatching.Sharder.dispatch_patterns(
      ["tesc1"], :worker4)

    #StringMatching.Sharder.chunk_patterns_rabin(
    #  ["tesk1","tesk2","tesk3","tesk4","tesk5","tesk6","tesk7"], {1,2}, 5)

    #StringMatching.Sharder.rebalance(
    #  ["tesk1","tesk2","tesk3","tesk4","tesk5","tesk6","tesk7"], 0, 5)

    StringMatching.Sharder.dispatch_patterns(
      ["tesk1","tesk2","tesk3","tesk4",
       "tesk5","tesk6","tesk7",
       "a","b","c","k","tes","kes","zob","ayr"])
  end
end
