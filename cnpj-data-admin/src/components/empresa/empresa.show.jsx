import { DateField, FunctionField, ReferenceField, Show, SimpleShowLayout, TextField, useGetOne, useRecordContext } from 'react-admin';

const Estabelicimento = () => {
    const record = useRecordContext();
    const { data: estabelecimento, isLoading, error } = useGetOne('estabelecimento', { id: record.cnpj_basico });

    if (isLoading) return <p>Loading...</p>;
    if (error) return <p>Error...</p>;

    return (
        <SimpleShowLayout record={estabelecimento}>
            <h2>Estabelecimento</h2>

            <FunctionField label="CNPJ" render={record => `${record.cnpj_basico}-${record.cnpj_ordem}/${record.cnpj_dv}`} />

            <TextField source="identificador_matriz_filial" />

            <TextField source="nome_fantasia" />

            <TextField source="situacao_cadastral" />
            <DateField source="data_situacao_cadastral" transform={v => v ? new Date(v) : null} />

            <TextField source="motivo_situacao_cadastral" />
            <TextField source="nome_cidade_exterior" />
            <TextField source="pais" />
            <TextField source="data_inicio_atividade" />
            <TextField source="cnae_fiscal_principal" />
            <TextField source="cnae_fiscal_secundaria" />
            <TextField source="tipo_logradouro" />
            <TextField source="logradouro" />
            <TextField source="numero" />
            <TextField source="complemento" />
            <TextField source="bairro" />
            <TextField source="cep" />
            <TextField source="uf" />
            <TextField source="municipio" />
            <TextField source="ddd_1" />
            <TextField source="telefone_1" />
            <TextField source="ddd_2" />
            <TextField source="telefone_2" />
            <TextField source="ddd_fax" />
            <TextField source="fax" />
            <TextField source="correio_eletronico" />
            <TextField source="situacao_especial" />
            <TextField source="data_situacao_especial" />
        </SimpleShowLayout>
    );
}


export const EmpresaShow = () => {

    return (
        <Show>
            <SimpleShowLayout>
                <h2>{'\t'}Empresa</h2>

                <TextField source="id" />
                <TextField source="cnpj_basico" />
                <TextField source="razao_social" />
                <ReferenceField source="natureza_juridica" reference="natju" label="Natureza Jurídica" />
                <ReferenceField source="qualificacao_responsavel" reference="quals" label="Qualificação do Responsável" />
                <TextField source="capital_social" />
                <TextField source="porte_empresa" />
                <TextField source="ente_federativo_responsavel" />

                <Estabelicimento />
            </SimpleShowLayout>
        </Show>
    );
}