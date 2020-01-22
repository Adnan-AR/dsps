defmodule RabinKarp.Server do
  @moduledoc """
  String matching worker as a GenServer (Rabin-Karp).
  """
  @behaviour StringMatching.Server.Interface.Behaviour
  use GenServer
  require Logger

  @doc """
  API: start an StringMatching process
  """
  def start_link(name, length) do
    Logger.info("StringMatching server created: #{name}")
    GenServer.start_link(__MODULE__, length, name: via(name))
  end

  @doc """
  API: stop the automaton
  """
  def stop(name), do: GenServer.stop(via(name))
 
  @doc """
  API: crash
  """
  def crash(name), do: GenServer.cast(via(name), :raise)

  @doc """
  API: create automaton from patterns
  """
  def update(name, pattern),
    do: GenServer.cast(via(name), {:add, pattern})

  @doc """
  API: search for patterns in a given string
  """
  def search(name, string) do
    GenServer.call(via(name), {:search, name, string})
  end

  
  # Callbacks
  @doc """
  Callback: Init the OTP server
  """
  def init(length) do
    Logger.info(
      "Starting Rabin-Karp server [length: #{inspect(length)}]")
    {:ok, RabinKarp.new(length)}
  end

  @doc """
  API: terminate StringMatching worker
  """
  def terminate(reason, name) do
    Logger.info("terminate: #{name} with reason: #{inspect reason}")
  end
  
  @doc """
  Create StringMatching automaton
  """
  def handle_cast({:add, pattern}, state) when is_binary(pattern) do
    new_state = RabinKarp.add(state, pattern)
    {:noreply, new_state}
  end
  def handle_cast({:add, pattern}, state) do
    new_state = RabinKarp.add(state, pattern, state.length)
    {:noreply, new_state}
  end

  @doc """
  Handle crash and raise
  """
  def handle_cast(:raise, name),
    do: raise RuntimeError, message: "Error, Server #{name} has crashed"

  @doc """
  Search for patterns in a string
  """
  def handle_call({:search, _name, string}, _from, state) do
    results = RabinKarp.search(state, string)
    |> MapSet.to_list    
    {:reply, results, state}
  end

  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: StringMatching.Servers.Registry.via(name)
  
end
