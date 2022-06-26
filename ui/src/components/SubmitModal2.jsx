import React from 'react';
import { Steps, Button, FlexLayout, FlexItem, StackingLayout, 
  Modal, FormItemInput, TextLabel , Select} from '@nutanix-ui/prism-reactjs';

  const customSuffix = (
    <FlexLayout alignItems="center" itemSpacing="10px">
      <TextLabel style={ { borderLeft: '1px solid #b8bfca',
        padding: '5px 0px 5px 10px' } }>GB</TextLabel>
    </FlexLayout>
  );
  
export default class SubmitModal2 extends React.Component {

    constructor(props) {
      super(props);
  
      this.state = {
        visible: false,
        inputArray: Array(5)
      };
  
      this.handleOnClose = this.handleOnClose.bind(this);
    }
  
    handleOnClose() {
      this.setState({ visible: false })
    }
    render() {
      return (
      console.log(this.state.inputArray),
        <div>
          <Button type="primary" margin-top='50px'
            onClick={ () => this.setState({ visible: true }) }>
            Give Inputs
          </Button>
          <Modal
            visible={ this.state.visible }
            title="Input"
            onClose={ this.handleOnClose }
            closeIconProps={ { 'data-test': 'my-close-icon-data-test' } }
            primaryButtonOnClick={ this.handleOnClose }
          >
            <StackingLayout padding="20px">
              <FormItemInput id="1" label="Intance type" placeholder="instance" defaultValue={this.state.inputArray[1]} />
              <FormItemInput id="5" label="Cloud Provider" placeholder="Cloud"  defaultValue={this.state.inputArray[4]}  />
            </StackingLayout>
          </Modal>
        </div>
      );
    }
}