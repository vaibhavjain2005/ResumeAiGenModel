import React from 'react'
import { Form, Input, Button } from "@heroui/react";
function PersonalDataForm() {

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const personal = {
            name: formData.get("name"),
            email: formData.get("email"),
            phone: formData.get("phone"),
        };
        console.log(personal);
        // Do something with the personal object
    };


    return (
        <Form onSubmit={handleSubmit}>
            <Input label="Name" name="name" isRequired />
            <Input label="Email" name="email" type="email" isRequired />
            <Input label="Phone" name="phone" type="tel" isRequired />
        </Form>
    )
}

export default PersonalDataForm 