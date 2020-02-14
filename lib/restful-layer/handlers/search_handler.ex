defmodule SearchHandler do  
  def init(_type, req, _opts) do
    # Init Client
    Client.Constructor.start(:ok,:ok)
    # nostate
    {:ok, req, :nostate}
  end

  def handle(request, state) do
    # Get the data from the body of the request
    {:ok, data, request0} = :cowboy_req.body(request)
    # Decode Json and get the data
    string = data
    |> Poison.decode!
    |> Map.get("haystack") 
    # Perform the search and transform the results to json
    res = Client.EndPoint.match(string)
    |> Enum.reduce(%{}, fn {x,y}, acc -> Map.put(acc, x,y) end)
    |> Poison.encode!
    # Reply
    { :ok, reply } = :cowboy_req.reply(
       200, [{"content-type", "text/html"}], res, request
    )
    {:ok, reply, state}
  end

  def terminate(_reason, _request, _state), do:    :ok
end
