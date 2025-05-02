import React, { useState, useRef, useEffect } from 'react';

import { Admin, ListGuesser, Resource, ShowGuesser } from "react-admin";

import Keycloak from 'keycloak-js';
import { keycloakAuthProvider, httpClient } from 'ra-keycloak';
import postgrestRestProvider, { defaultSchema } from '@raphiniert/ra-data-postgrest';
import { EmpresaList } from './components/empresa/empresa.list';
import { EstabelecimentoList } from './components/estabelicimento.list';
import { SocioList } from './components/socios.list';
import { SimpleList } from './components/simples.list';
import { KeyValueList } from './components/keyvalue.list';
import UserIcon from '@mui/icons-material/People';
import { EmpresaShow } from './components/empresa/empresa.show';

const config = {
  url: import.meta.env.VITE_OIDC_ENDPOINT,
  realm: import.meta.env.VITE_OIDC_REALM,
  clientId: import.meta.env.VITE_OIDC_CLIENT,
};

const MyAdmin = () => {
  const [keycloak, setKeycloak] = useState();
  const authProvider = useRef();
  const dataProvider = useRef();

  useEffect(() => {
    const initKeyCloakClient = async () => {
      const keycloakClient = new Keycloak(config);
      await keycloakClient.init({ onLoad: 'login-required' });

      authProvider.current = keycloakAuthProvider(
        keycloakClient
      );

      dataProvider.current = postgrestRestProvider({
        apiUrl: import.meta.env.VITE_API_URL,
        httpClient: httpClient(keycloakClient),
        defaultListOp: 'eq',
        primaryKeys: new Map([
          ['empresa', ['cnpj_basico']],
          ['estabelecimento', ['cnpj_basico']],
          ['socios', ['cnpj_basico']],
          ['simples', ['cnpj_basico']],
          ['cnae', ['codigo']],
          ['natju', ['codigo']],
          ['pais', ['codigo']],
          ['moti', ['codigo']],
          ['munic', ['codigo']],
          ['quals', ['codigo']],
        ]),
        schema: defaultSchema
      });

      setKeycloak(keycloakClient);
    };

    if (!keycloak) {
      initKeyCloakClient();
    }
  }, [keycloak]);

  if (!keycloak) return <p>Loading...</p>;

  return (
    <Admin
      basename="/admin"
      dataProvider={dataProvider.current}
      authProvider={authProvider.current}>
      <Resource name="empresa" list={EmpresaList} show={EmpresaShow} icon={UserIcon}  />
      <Resource name="estabelecimento" list={EstabelecimentoList} show={ShowGuesser} />
      <Resource name="socios" list={SocioList} />
      <Resource name="simples" list={SimpleList} />
      <Resource name="cnae" list={KeyValueList} />
      <Resource name="natju" list={KeyValueList} />
      {/* <Resource name="natju" list={ListGuesser} recordRepresentation={(record) => `${record.descricao}`} /> */}
      <Resource name="pais" list={KeyValueList} />
      <Resource name="moti" list={KeyValueList} />
      <Resource name="munic" list={KeyValueList} />
      {/* <Resource name="quals" list={ListGuesser} recordRepresentation={(record) => `${record.descricao}`} /> */}
      <Resource name="quals" list={KeyValueList} />
    </Admin>
  );
}

export default MyAdmin;