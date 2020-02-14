defmodule ChunkIt do
  def load_chunk_2 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_2.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(200000000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> MapSet.new
    #|> Helpers.Hash.chunk_patterns_byworkers([:a,:b,:c])
    # |> Helpers.Hash.groupby_length
    #|> Enum.each(fn {x, y} -> Helpers.Hash.chunk_patterns(y, 3) end)
  end
end
