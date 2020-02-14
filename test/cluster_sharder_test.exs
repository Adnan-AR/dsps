defmodule Cluster.SharderTest do
  use ExUnit.Case, async: true
  doctest Cluster.Sharder

  
  describe "chunk_patterns_byworkers/2 in patterns_handler same size" do
    test "[PYTHON] test via erlport: Distribute small list
          with the same size over nodes" do
      # Starting Python process
      {:ok, pid_python} = :python.start(
	[{:python_path, 'lib/master'}, {:python, 'python3'}])
      # workers
      workers = ["worker1", "worker2", "worker3", "worker4"]
      # Patterns
      patterns = ["test1", "test2", "test3"]
      # Expected worker's states
      expected_shards = %{
	"worker1" => ["test1"],
	"worker2" => ["test2"],
	"worker3" => ["test3"]
      }
      # Calling the python function
      results = :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers',
	[patterns, workers])
      # Assert
      assert (results == expected_shards)
    end
  end

  describe "chunk_patterns_byworkers/2 in patterns_handler different size" do
    test "[PYTHON] test via erlport: Distribute small list
          with different size over nodes" do
      # Starting Python process
      {:ok, pid_python} = :python.start(
	[{:python_path, 'lib/master'}, {:python, 'python3'}])
      # workers
      workers = ["worker1", "worker2", "worker3", "worker4"]
      # Patterns
      patterns = ["test1", "test2", "test31"]
      # Expected worker's states
      expected_shards = %{
	"worker1" => ["test1", "test31"],
	"worker2" => ["test2"]
      }
      # Calling the python function
      results = :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers',
	[patterns, workers])
      # Assert
      assert (results == expected_shards)
    end
  end

  describe "chunk_patterns_byworkers/2 in patterns_handler same 
           size same number of nodes (num patterns == num workers)" do
    test "[PYTHON] test via erlport: Distribute small list
          with different size over nodes" do
      # Starting Python process
      {:ok, pid_python} = :python.start(
	[{:python_path, 'lib/master'}, {:python, 'python3'}])
      # workers
      workers = ["worker1", "worker2", "worker3", "worker4"]
      # Patterns
      patterns = ["test1", "test2", "test3", "test4"]
      # Expected worker's states
      expected_shards = %{
	"worker1" => ["test1"],
	"worker2" => ["test2"],
	"worker3" => ["test3"],
	"worker4" => ["test4"]
      }
      # Calling the python function
      results = :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers',
	[patterns, workers])
      # Assert
      assert (results == expected_shards)
    end
  end

   describe "chunk_patterns_byworkers/2 in patterns_handler different
           size same number of nodes (num patterns == num workers)" do
    test "[PYTHON] test via erlport: Distribute small list
          with different size over nodes" do
      # Starting Python process
      {:ok, pid_python} = :python.start(
	[{:python_path, 'lib/master'}, {:python, 'python3'}])
      # workers
      workers = ["worker1", "worker2", "worker3", "worker4"]
      # Patterns
      patterns = ["test1", "test2", "test13", "test4"]
      # Expected worker's states
      expected_shards = %{
	"worker1" => ["test1", "test13"],
	"worker2" => ["test2"],
	"worker3" => ["test4"]
      }
      # Calling the python function
      results = :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers',
	[patterns, workers])
      # Assert
      assert (results == expected_shards)
    end
  end

   describe "chunk_patterns_byworkers/2 in patterns_handler different
           size same number of nodes (num patterns > num workers)" do
    test "[PYTHON] test via erlport: Distribute small list
          with different size over nodes" do
      # Starting Python process
      {:ok, pid_python} = :python.start(
	[{:python_path, 'lib/master'}, {:python, 'python3'}])
      # workers
      workers = ["worker1", "worker2", "worker3", "worker4"]
      # Patterns
      patterns = ["test1", "test2", "test13",
		  "test4", "test14", "test15",
		  "test16", "test5"]
      # Expected worker's states
      expected_shards = %{
	"worker1" => ["test1", "test13"],
	"worker2" => ["test2", "test14"],
	"worker3" => ["test4", "test15"],
	"worker4" => ["test5", "test16"]
      }
      # Calling the python function
      results = :python.call(
	pid_python, :patterns_handler,
	:'PatternsHandler.chunk_patterns_byworkers',
	[patterns, workers])
      # Assert
      assert (results == expected_shards)
    end
   end


end
