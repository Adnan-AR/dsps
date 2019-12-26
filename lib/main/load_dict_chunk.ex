defmodule DictLoader do
  def load_chunk(file_name) do
    "/Users/adnan/Qemotion/dsps_system/tmp_dict/#{file_name}"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    # |> Enum.take(100000)
    |> Enum.map(fn x -> Enum.at(x,0) end)
    |> StringMatching.Sharder.dispatch_patterns
  end

  def load_chunk_2 do
    "/Users/adnan/Qemotion/dsps_system/tmp_data2/1000k_words_2.csv"
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(50)
    |> Enum.map(fn x -> Enum.at(x,0) end)
  end
end


