import { Datagrid, DateField, List, TextField, TextInput } from 'react-admin';

export const SimpleList = () => (
    <List filters={[<TextInput label="Search" source="cnpj_basico" alwaysOn />]}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="cnpj_basico" />
            <TextField source="opcao_pelo_simples" />
            <TextField source="data_opcao_simples" />
            <TextField source="data_exclusao_simples" />
            <TextField source="opcao_mei" />
            <TextField source="data_opcao_mei" />
            <TextField source="data_exclusao_mei" />
        </Datagrid>
    </List>
);