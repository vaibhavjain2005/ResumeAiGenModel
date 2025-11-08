import './App.css'
import NavBar from './components/NavBar'
import { Card, CardBody, CardFooter } from "@heroui/react";
import { Button } from "@heroui/react";

import { Link } from "react-router-dom";
import '@fontsource/momo-signature';
function App() {


  return (
    <>
      <div className="flex flex-col justify-center items-center h-dvh">
        <Card className="w-11/12 h-9/12 text-center bg-[url('https://images.unsplash.com/photo-1654198340681-a2e0fc449f1b?ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&q=80&w=1470')] bg-cover bg-center " >
          <div class="absolute inset-0 bg-black/50"></div>
          <CardBody className='p-10'>
            <h1 style={{ fontFamily: '"Momo Signature", cursive' }} className='text-6xl'>ResumeChef.</h1>
            <h1 className="text-3xl font-bold mb-2 pt-10">Welcome to ResumeChef.</h1>
            <p className="text-lg text-gray-600 mb-8">
              A dynamic resume builder which adapts itself to different Job Descriptions.
            </p>
          </CardBody>
          <CardFooter >
            <Link to={'/get-started'} className="flex flex-col justify-center w-full">
              <Button color="primary" size='lg' className='w-4/12 mb-10'>
                Get Started
              </Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    </>
  )
}

export default App
