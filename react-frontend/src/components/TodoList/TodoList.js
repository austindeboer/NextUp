import React from 'react';
import { List } from 'antd';
import { TodoTask } from '../TodoTask/TodoTask';

export const TodoList = ({ todos }) => (
  <List
    locale={{
      emptyText: "There are no todo's",
    }}
    dataSource={todos}
    renderItem={todo => <TodoTask todo={todo} />}
    pagination={{
      position: 'bottom',
      pageSize: 10,
    }}
  />
);
