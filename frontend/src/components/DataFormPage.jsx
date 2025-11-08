import { Card, Form } from '@heroui/react';
import { Input, Textarea } from '@heroui/react';  // or from '@heroui/input' if separate
import { Button } from '@heroui/react';
import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from "lucide-react";
function DataFormPage() {
    const [jobDesc, setJobDesc] = useState('');
    const [personal, setPersonal] = useState({ name: '', email: '', phone: '' });
    const [edu, setEdu] = useState([{ degree: '', university: '', year: '' }]);
    const [exp, setExp] = useState([{ title: '', company: '', duration: '', description: '' }]);
    const [proj, setProj] = useState([{ name: '', technologies: '', description: '' }]);
    const [skills, setSkills] = useState('');

    // Handlers for dynamic arrays
    const handleEduChange = (index, field, value) => {
        const newArr = [...edu];
        newArr[index][field] = value;
        setEdu(newArr);
    };

    const addEdu = () => {
        setEdu([...edu, { degree: '', university: '', year: '' }]);
    };

    const handleExpChange = (i, field, value) => {
        const newArr = [...exp];
        newArr[i][field] = value;
        setExp(newArr);
    };

    const addExp = () => {
        setExp([...exp, { title: '', company: '', duration: '', description: '' }]);
    };

    const handleProjChange = (i, field, value) => {
        const newArr = [...proj];
        newArr[i][field] = value;
        setProj(newArr);
    };

    const addProj = () => {
        setProj([...proj, { name: '', technologies: '', description: '' }]);
    };

    // On Submit
    const handleSubmit = (e) => {
        e.preventDefault();
        const obj = {
            job_desc: jobDesc,
            personal,
            edu,
            exp,
            proj,
            skills: skills.split(',').map(s => s.trim()).filter(s => s)
        };
        console.log('Form output JSON:', JSON.stringify(obj, null, 2));

    };

    return (
        <div className='flex flex-col w-full mt-20'>
            <div className='flex w-full justify-center'>
                <div className='flex w-8/12 justify-start'>
                    <Link to={'/'} className="flex items-center gap-2 text-white hover:text-gray-300">
                        <ArrowLeft className=" text-white" />
                        Back to Home
                    </Link>
                </div>
            </div>


            <div className='flex justify-center mt-10'>
                <Card className='w-8/12 justify-center mb-10'>
                    <Form onSubmit={handleSubmit} className="space-y-6 p-6">
                        {/* Job Description */}
                        <Textarea
                            label="Job Description"
                            name="job_desc"
                            value={jobDesc}
                            onChange={(e) => setJobDesc(e.target.value)}
                            isRequired
                            description="Enter the full job description text."
                        />

                        {/* Personal Info */}
                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Personal Details</h3>
                            <Input
                                label="Name"
                                name="personal_name"
                                value={personal.name}
                                onChange={(e) => setPersonal({ ...personal, name: e.target.value })}
                                isRequired
                            />
                            <Input
                                label="Email"
                                name="personal_email"
                                type="email"
                                value={personal.email}
                                onChange={(e) => setPersonal({ ...personal, email: e.target.value })}
                                isRequired
                            />
                            <Input
                                label="Phone"
                                name="personal_phone"
                                value={personal.phone}
                                onChange={(e) => setPersonal({ ...personal, phone: e.target.value })}
                                isRequired
                            /></div>


                        {/* Education */}
                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Education</h3>
                            {edu.map((eItem, idx) => (
                                <div key={idx} className="space-y-2">
                                    <Input
                                        label="Degree"
                                        value={eItem.degree}
                                        onChange={(ev) => handleEduChange(idx, 'degree', ev.target.value)}
                                        isRequired
                                    />
                                    <Input
                                        label="University"
                                        value={eItem.university}
                                        onChange={(ev) => handleEduChange(idx, 'university', ev.target.value)}
                                        isRequired
                                    />
                                    <Input
                                        label="Year"
                                        value={eItem.year}
                                        onChange={(ev) => handleEduChange(idx, 'year', ev.target.value)}
                                        isRequired
                                    />
                                </div>
                            ))}
                            <Button type="button" onPress={addEdu} color="secondary" size="sm">
                                + Add Education
                            </Button>
                        </div>

                        {/* Experience */}
                        <div className="space-y-4 w-full" >
                            <h3 className="text-xl font-semibold">Experience</h3>
                            {exp.map((xItem, idx) => (
                                <div key={idx} className="space-y-2 p-4 rounded">
                                    <Input
                                        label="Title"
                                        value={xItem.title}
                                        onChange={(ev) => handleExpChange(idx, 'title', ev.target.value)}
                                        isRequired
                                    />
                                    <Input
                                        label="Company"
                                        value={xItem.company}
                                        onChange={(ev) => handleExpChange(idx, 'company', ev.target.value)}
                                        isRequired
                                    />
                                    <Input
                                        label="Duration"
                                        value={xItem.duration}
                                        onChange={(ev) => handleExpChange(idx, 'duration', ev.target.value)}
                                        isRequired
                                    />
                                    <Textarea
                                        label="Description"
                                        value={xItem.description}
                                        onChange={(ev) => handleExpChange(idx, 'description', ev.target.value)}
                                        isRequired
                                    />
                                </div>
                            ))}
                            <Button type="button" onPress={addExp} color="secondary" size="sm">
                                + Add Experience
                            </Button>
                        </div>

                        {/* Projects */}
                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Projects</h3>
                            {proj.map((pItem, idx) => (
                                <div key={idx} className="space-y-2  p-4 rounded">
                                    <Input
                                        label="Project Name"
                                        value={pItem.name}
                                        onChange={(ev) => handleProjChange(idx, 'name', ev.target.value)}
                                        isRequired
                                    />
                                    <Input
                                        label="Technologies"
                                        value={pItem.technologies}
                                        onChange={(ev) => handleProjChange(idx, 'technologies', ev.target.value)}
                                        isRequired
                                    />
                                    <Textarea
                                        label="Description"
                                        value={pItem.description}
                                        onChange={(ev) => handleProjChange(idx, 'description', ev.target.value)}
                                        isRequired
                                    />
                                </div>
                            ))}
                            <Button type="button" onPress={addProj} color="secondary" size="sm">
                                + Add Project
                            </Button>
                        </div>

                        {/* Skills */}
                        <Input
                            label="Skills (comma separated)"
                            name="skills"
                            value={skills}
                            onChange={(e) => setSkills(e.target.value)}
                            placeholder="e.g. JavaScript, Python, React, AWS"
                            isRequired
                        />

                        {/* Submit */}
                        <Button type="submit" color="primary" size="lg" className="w-full">
                            Submit
                        </Button>
                    </Form>
                </Card>
            </div>
        </div>


    );
}

export default DataFormPage 