import { Datagrid, List, NumberField, TextField, TextInput } from 'react-admin';

export const EmpresaList = () => (
    <List filters={[<TextInput label="Search" source="cnpj_basico" alwaysOn />]}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="cnpj_basico" />
            <TextField source="razao_social" />
            <NumberField source="natureza_juridica" />
            <NumberField source="qualificacao_responsavel" />
            <NumberField source="capital_social" />
        </Datagrid>
    </List>
);