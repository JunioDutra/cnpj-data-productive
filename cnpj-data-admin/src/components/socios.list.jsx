import { Datagrid, DateField, List, TextField, TextInput } from 'react-admin';

export const SocioList = () => (
    <List filters={[<TextInput label="Search" source="cnpj_basico" alwaysOn />]}>
        <Datagrid rowClick="edit">
            <TextField source="id" />
            <TextField source="cnpj_basico" />
            <TextField source="nome_socio_razao_social" />
            <TextField source="cpf_cnpj_socio" />
            <TextField source="data_entrada_sociedade" />
            <TextField source="representante_legal" />
            <TextField source="nome_do_representante" />
        </Datagrid>
    </List>
);