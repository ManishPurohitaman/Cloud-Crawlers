import React from 'react';
import { Select } from '@nutanix-ui/prism-reactjs';

const data = [
  {
    key: 1,
    label: 'puppyfood'
  },
  {
    key: 2,
    label: 'Peach'
  },
  {
    key: 3,
    label: 'galesbure'
  }
];

export default class MySelect extends React.Component {

  constructor(props) {
    super(props);

    this.state = {
      selectedRow: null
    };

    this.handleOnSelectedChange = this.handleOnSelectedChange.bind(this);
    this.selectProps = {
      rowsData: data,
      onSelectedChange: this.handleOnSelectedChange,
      // We attached to the right-panel to handle the scrolling placement properly.
      getPopupContainer: () => document.querySelector('.right-panel'),
      popupProviderProps: { action: 'hover' }
    }
    
  }
    
  handleOnSelectedChange(selectedRow) {
    this.setState({ selectedRow });
  }

  render() {
    return (
      <Select style={ { maxWidth: '440px' } }
        { ...this.selectProps }
        selectedRow={ this.state.selectedRow }
      />
    );
  }

}