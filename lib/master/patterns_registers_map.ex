defmodule Patterns.Registers.Map do
  @moduledoc """
  Agent to store node registers names.
  """
  use Agent
  @name __MODULE__
  
  @doc """
  Start the Metadata base
  """
  def start_link(registers_names) do
    fn -> registers_names end
    |> Agent.start_link(name: @name)
  end

  @doc """
  Get the list of patterns registers
  """
  def get,
    do: Agent.get(@name, fn registers -> registers end)
  
  @doc """
  Get the list of patterns registers of a certain length
  """
  def get(length) do
    getter = fn registers ->
      Map.get(registers, length)
    end
    Agent.get(@name, getter)
  end


  @doc """
  add register with a specific length
  """
  # l stands for length
  # new_r stands for new register
  def add_register(new_r, l) do
    handle_update = fn
      registers ->
	Map.put(registers, l, new_r)
    end
    Agent.update(@name, handle_update)
  end
end
