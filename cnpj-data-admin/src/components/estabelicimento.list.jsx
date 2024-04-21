import { Datagrid, DateField, List, TextField, TextInput } from 'react-admin';

export const EstabelecimentoList = () => (
    <List filters={[<TextInput label="Search" source="cnpj_basico" alwaysOn />]}>
        <Datagrid rowClick="show">
            <TextField source="id" />
            <TextField source="cnpj_basico" />
            <TextField source="identificador_matriz_filial" />
            <TextField source="nome_fantasia" />
            <DateField source="data_inicio_atividade" />
            <TextField source="ddd_1" />
            <TextField source="telefone_1" />
            <TextField source="correio_eletronico" />
        </Datagrid>
    </List>
);