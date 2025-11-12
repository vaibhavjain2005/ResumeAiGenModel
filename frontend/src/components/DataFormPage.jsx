import { Card, Form, Input, Textarea, Button } from '@heroui/react';
import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft } from "lucide-react";

function DataFormPage() {
    const navigate = useNavigate();

    // 🧠 Default sample data
    const [jobDesc, setJobDesc] = useState(`We are looking for a Python Developer with experience in Machine Learning and NLP. Required skills: Python, TensorFlow, PyTorch, NLP, API development, Flask.`);
    const [personal, setPersonal] = useState({
        name: 'John Doe',
        email: 'john@example.com',
        phone: '+1234567890'
    });
    const [edu, setEdu] = useState([
        { degree: 'Bachelor of Computer Science', university: 'Example University', year: '2020' }
    ]);
    const [exp, setExp] = useState([
        {
            title: 'Software Developer',
            company: 'Tech Corp',
            duration: '2020-2023',
            description: 'Developed scalable web applications using Python and Flask, improving efficiency and system performance.'
        }
    ]);
    const [proj, setProj] = useState([
        {
            name: 'NLP Chatbot',
            technologies: 'Python, TensorFlow, NLP',
            description: 'Built a chatbot using NLP and TensorFlow to automate customer interactions and improve efficiency.'
        },
        {
            name: 'ML Image Classifier',
            technologies: 'Python, PyTorch, CNN',
            description: 'Implemented an image classification model using PyTorch to enhance visual recognition accuracy.'
        }
    ]);
    const [skills, setSkills] = useState('Python, NLP, TensorFlow, PyTorch, Flask, AWS, Docker, SQL, React');
    const [loading, setLoading] = useState(false);

    // Handlers
    const handleEduChange = (index, field, value) => {
        const newArr = [...edu];
        newArr[index][field] = value;
        setEdu(newArr);
    };
    const addEdu = () => setEdu([...edu, { degree: '', university: '', year: '' }]);

    const handleExpChange = (index, field, value) => {
        const newArr = [...exp];
        newArr[index][field] = value;
        setExp(newArr);
    };
    const addExp = () => setExp([...exp, { title: '', company: '', duration: '', description: '' }]);

    const handleProjChange = (index, field, value) => {
        const newArr = [...proj];
        newArr[index][field] = value;
        setProj(newArr);
    };
    const addProj = () => setProj([...proj, { name: '', technologies: '', description: '' }]);

    // Submit
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        const obj = {
            job_description: jobDesc,
            personal_info: personal,
            education: edu,
            experience: exp,
            projects: proj,
            skills: skills.split(',').map(s => s.trim()).filter(s => s)
        };

        try {
            // 🔥 Replace with your backend endpoint
            const response = await fetch('http://localhost:8000/generate-resume', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(obj)
            });

            const data = await response.json();

            // Navigate to /result with the JSON data
            navigate('/result', { state: { result: data } });
        } catch (error) {
            console.error('Error submitting data:', error);
            alert('Failed to connect to the server.');
        } finally {
            setLoading(false);
        }
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
                        <Textarea
                            label="Job Description"
                            value={jobDesc}
                            onChange={(e) => setJobDesc(e.target.value)}
                            isRequired
                            description="Enter the full job description text."
                        />

                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Personal Details</h3>
                            <Input label="Name" value={personal.name} onChange={(e) => setPersonal({ ...personal, name: e.target.value })} isRequired />
                            <Input label="Email" type="email" value={personal.email} onChange={(e) => setPersonal({ ...personal, email: e.target.value })} isRequired />
                            <Input label="Phone" value={personal.phone} onChange={(e) => setPersonal({ ...personal, phone: e.target.value })} isRequired />
                        </div>

                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Education</h3>
                            {edu.map((eItem, idx) => (
                                <div key={idx} className="space-y-2">
                                    <Input label="Degree" value={eItem.degree} onChange={(e) => handleEduChange(idx, 'degree', e.target.value)} />
                                    <Input label="University" value={eItem.university} onChange={(e) => handleEduChange(idx, 'university', e.target.value)} />
                                    <Input label="Year" value={eItem.year} onChange={(e) => handleEduChange(idx, 'year', e.target.value)} />
                                </div>
                            ))}
                            <Button type="button" onPress={addEdu} color="secondary" size="sm">
                                + Add Education
                            </Button>
                        </div>

                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Experience</h3>
                            {exp.map((xItem, idx) => (
                                <div key={idx} className="space-y-2">
                                    <Input label="Title" value={xItem.title} onChange={(e) => handleExpChange(idx, 'title', e.target.value)} />
                                    <Input label="Company" value={xItem.company} onChange={(e) => handleExpChange(idx, 'company', e.target.value)} />
                                    <Input label="Duration" value={xItem.duration} onChange={(e) => handleExpChange(idx, 'duration', e.target.value)} />
                                    <Textarea label="Description" value={xItem.description} onChange={(e) => handleExpChange(idx, 'description', e.target.value)} />
                                </div>
                            ))}
                            <Button type="button" onPress={addExp} color="secondary" size="sm">
                                + Add Experience
                            </Button>
                        </div>

                        <div className="space-y-4 w-full">
                            <h3 className="text-xl font-semibold">Projects</h3>
                            {proj.map((pItem, idx) => (
                                <div key={idx} className="space-y-2">
                                    <Input label="Project Name" value={pItem.name} onChange={(e) => handleProjChange(idx, 'name', e.target.value)} />
                                    <Input label="Technologies" value={pItem.technologies} onChange={(e) => handleProjChange(idx, 'technologies', e.target.value)} />
                                    <Textarea label="Description" value={pItem.description} onChange={(e) => handleProjChange(idx, 'description', e.target.value)} />
                                </div>
                            ))}
                            <Button type="button" onPress={addProj} color="secondary" size="sm">
                                + Add Project
                            </Button>
                        </div>

                        <Input
                            label="Skills (comma separated)"
                            value={skills}
                            onChange={(e) => setSkills(e.target.value)}
                            placeholder="e.g. Python, React, AWS"
                            isRequired
                        />

                        <Button type="submit" color="primary" size="lg" className="w-full" isLoading={loading}>
                            {loading ? 'Processing...' : 'Submit'}
                        </Button>
                    </Form>
                </Card>
            </div>
        </div>
    );
}

export default DataFormPage;
