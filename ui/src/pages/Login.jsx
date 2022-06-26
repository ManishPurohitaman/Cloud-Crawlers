import * as React from "react";
import { Route, BrowserRouter } from "react-router-dom";
import ReactDOM from "react-dom";
import _ from 'lodash';

import { Title, StackingLayout, FormItemInput, Button, Divider, Paragraph,
    FlexLayout, Link } from '@nutanix-ui/prism-reactjs';


export default class Login extends React.Component {
    constructor(props) {
        super(props);
    }

    render(){
        return (
        <FlexLayout style={ { height: '500px' } } alignItems="center" justifyContent="center">
        <StackingLayout style={ { width: '280px' } } itemSpacing="30px">
          <Title>Welcome to Nutanix</Title>
          <StackingLayout>
            <FormItemInput id="username" label="Username" placeholder="Username" />
            <FormItemInput id="password" label="Password" placeholder="Password"
              helpText={ <Link size="small">Forgot Password?</Link> }
            />
          </StackingLayout>
          <Button fullWidth={ true }>Log In</Button>
          <StackingLayout>
            <FlexLayout alignItems="center">
              <Divider />
              <Paragraph className="no-wrap" type="secondary">New to Nutanix?</Paragraph>
              <Divider />
            </FlexLayout>
            <Button fullWidth={ true } type="secondary">Sign Up</Button>
          </StackingLayout>
        </StackingLayout>
      </FlexLayout>
        )
    }
}