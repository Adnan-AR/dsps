defmodule UpdateHandler do  
  def init(_type, req, _opts) do
    # Init one sharder
    Cluster.Sharder.start_link(:whatever)
    # nostate
    {:ok, req, :nostate}
  end

  def handle(request, state) do
    # Get the data from the body of the request
    {:ok, data, request0} = :cowboy_req.body(request)
    # Decode Json and get the needles
    patterns = data
    |> Poison.decode!
    |> Map.get("patterns") 
    # Add patterns to cluster via the :whatever sharder
    Cluster.Sharder.dispatch_patterns(patterns, :whatever)
    # Reply
    { :ok, reply } = :cowboy_req.reply(
      200, [{"content-type", "text/html"}], "<h1>Done</h1>", request
    )
    {:ok, reply, state}
  end

  def terminate(_reason, _request, _state), do:    :ok
end
