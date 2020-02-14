defmodule StringMatching.Sharder.Interface do
  @moduledoc """
  Sharder server interface.
  """
  @local_sharder StringMatching.Sharder
  defmodule Behaviour do
    @callback start_link(any()) :: {:ok, Pid.t()} | {:error, term}
    @callback stop(String.t) :: :ok | {:error, String.t()}
    @callback crash(String.t) :: :ok | {:erro, String.t()}
    @callback dispatch_patterns(list(String.t) | String.t) :: :ok
                                               | {:error, String.t()}
    @callback dispatch_patterns(list(String.t) | String.t, String.t)
					       :: :ok
                                               | {:error, String.t()}
    @callback fully_search(String.t) :: list(Tuple.t) | List.t
  end

  @spec start_link(any()) :: {:ok, Pid.t()} | {:error, term}
  def start_link(_arg), do: @local_sharder.start_link(_arg)
  @spec stop(String.t) :: :ok | {:error, String.t()}
  def stop(name), do: @local_sharder.stop(name)
  @spec crash(String.t) :: :ok | {:erro, String.t()}
  def crash(name), do: @local_sharder.stop(name)
  @spec dispatch_patterns(list(String.t) | String.t, String.t) :: :ok
                                         | {:error, String.t()}
  def dispatch_patterns(patterns, worker_name) do
    @local_sharder.dispatch_patterns(patterns, worker_name)
  end
  @spec dispatch_patterns(list(String.t) | String.t) :: :ok
                                         | {:error, String.t()}
  def dispatch_patterns(patterns),
    do: @local_sharder.dispatch_patterns(patterns)
  @spec fully_search(String.t) :: list(Tuple.t) | List.t
  def fully_search(string), do: @local_sharder.fully_search(string)
end
