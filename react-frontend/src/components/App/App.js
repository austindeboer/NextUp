import React, { useState } from 'react';
import { useEffect } from 'react';

import './App.css';
import { ChakraProvider, theme } from '@chakra-ui/react';
import Header from '../Header/Header';
import TodoTask from '../TodoTask/TodoTask';
import { TodoList } from '../TodoList/TodoList';

// finish this

function App() {
  const [todoList, setTodoList] = useState();

  const [todos, setTodos] = useState([]);

  const fetchTodos = async () => {
    const response = await fetch('http://127.0.0.1:8000/todos');
    const todos = await response.json();
    console.log(todos);
    setTodos(todos);
  };

  useEffect(() => {
    fetchTodos();
  }, []);

  const handleToggle = id => {
    let mapped = todoList.map(task => {
      return task.id === Number(id)
        ? { ...task, completed: !task.completed }
        : { ...task };
    });
    setTodoList(mapped);
  };

  const handleFilter = () => {
    let filtered = todoList.filter(task => {
      return !task.completed;
    });
    setTodoList(filtered);
  };

  const addTask = userInput => {
    let copy = [...todoList];
    copy = [
      ...copy,
      { id: todoList.length + 1, task: userInput, completed: false },
    ];
    setTodoList(copy);
  };

  return (
    <ChakraProvider theme={theme}>
      <Header />
      <TodoList
        toDoList={todoList}
        handleToggle={handleToggle}
        handleFilter={handleFilter}
      />
    </ChakraProvider>
  );
}

export default App;
