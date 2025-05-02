import { Datagrid, List, TextField } from 'react-admin';

export const KeyValueList = () => (
    <List>
        <Datagrid>
            <TextField source="codigo" />
            <TextField source="descricao" />
        </Datagrid>
    </List>
);