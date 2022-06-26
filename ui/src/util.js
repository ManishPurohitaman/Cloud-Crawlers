import React from 'react';
import axios from 'axios';

const URL = 'http://127.0.0.1:5000/api/v1/vm/sizer?cpu=2&ram=2&region=us-east-1';

export async function getSubscription() {
  const data = await fetch(URL);
  const res = await data.json();
  console.log(res);
  return res;
}
 