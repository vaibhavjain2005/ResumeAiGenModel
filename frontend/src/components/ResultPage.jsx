import React from "react";
import { useLocation, Link } from "react-router-dom";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { Button, Card } from "@heroui/react";
import { ArrowLeft } from "lucide-react";

// Load custom Google font dynamically
const addCustomFont = () => {
    const link = document.createElement("link");
    link.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap";
    link.rel = "stylesheet";
    document.head.appendChild(link);
};

function ResultPage() {
    const location = useLocation();
    const result = location.state?.result;

    React.useEffect(() => {
        addCustomFont();
    }, []);

    if (!result) {
        return (
            <div className="flex flex-col items-center justify-center h-screen text-white">
                <h2>No data found. Please go back and submit the form.</h2>
                <Link to="/">
                    <Button color="primary" className="mt-4">
                        Go Back
                    </Button>
                </Link>
            </div>
        );
    }

    // 🧾 PDF Download
    const handleDownload = async () => {
        const element = document.getElementById("resume-content");

        // Increase scale for better PDF clarity
        const canvas = await html2canvas(element, { scale: 2, backgroundColor: "#ffffff" });
        const imgData = canvas.toDataURL("image/png");
        const pdf = new jsPDF("p", "mm", "a4");

        const pageWidth = pdf.internal.pageSize.getWidth();
        const pageHeight = pdf.internal.pageSize.getHeight();
        const imgWidth = pageWidth;
        const imgHeight = (canvas.height * pageWidth) / canvas.width;

        let position = 0;
        if (imgHeight < pageHeight) {
            pdf.addImage(imgData, "PNG", 0, 0, imgWidth, imgHeight);
        } else {
            let heightLeft = imgHeight;
            let y = 0;
            while (heightLeft > 0) {
                pdf.addImage(imgData, "PNG", 0, y, imgWidth, imgHeight);
                heightLeft -= pageHeight;
                if (heightLeft > 0) {
                    pdf.addPage();
                    y = -pageHeight;
                }
            }
        }

        pdf.save(`${result.personal_info.name}_resume.pdf`);
    };

    return (
        <div className="flex flex-col items-center mt-20 text-white">
            <div className="w-8/12 flex justify-start mb-4">
                <Link to="/" className="flex items-center gap-2 text-white hover:text-gray-300">
                    <ArrowLeft /> Back to Form
                </Link>
            </div>

            <Card className="w-8/12 p-8 bg-white text-black rounded-lg shadow-lg">
                {/* ===== Resume Content ===== */}
                <div
                    id="resume-content"
                    className="p-6"
                    style={{
                        fontFamily: "'Inter', sans-serif",
                        lineHeight: "1.6",
                        color: "#222",
                    }}
                >
                    {/* Header */}
                    <header className="mb-4 text-center border-b border-gray-300 pb-2">
                        <h1 className="text-3xl font-semibold mb-1">{result.personal_info.name}</h1>
                        <p className="text-gray-700 text-sm">
                            {result.personal_info.email} • {result.personal_info.phone}
                        </p>
                    </header>

                    {/* Professional Summary */}
                    {result.professional_summary && (
                        <section className="mb-5">
                            <h2 className="text-lg font-semibold border-b border-gray-400 pb-1 mb-2 text-gray-800 uppercase tracking-wide">
                                Professional Summary
                            </h2>
                            <p className="text-sm text-gray-700">{result.professional_summary}</p>
                        </section>
                    )}

                    {/* Education */}
                    {result.education?.length > 0 && (
                        <section className="mb-5">
                            <h2 className="text-lg font-semibold border-b border-gray-400 pb-1 mb-2 text-gray-800 uppercase tracking-wide">
                                Education
                            </h2>
                            {result.education.map((edu, idx) => (
                                <div key={idx} className="mb-2">
                                    <p className="font-semibold text-gray-900">{edu.degree}</p>
                                    <p className="text-sm text-gray-700">
                                        {edu.university} ({edu.year})
                                    </p>
                                </div>
                            ))}
                        </section>
                    )}

                    {/* Experience */}
                    {result.experience?.length > 0 && (
                        <section className="mb-5">
                            <h2 className="text-lg font-semibold border-b border-gray-400 pb-1 mb-2 text-gray-800 uppercase tracking-wide">
                                Experience
                            </h2>
                            {result.experience.map((exp, idx) => (
                                <div key={idx} className="mb-3">
                                    <p className="font-semibold text-gray-900">
                                        {exp.title} — {exp.company}
                                    </p>
                                    <p className="text-sm text-gray-600 mb-1">{exp.duration}</p>
                                    <p className="text-sm text-gray-700">{exp.description}</p>
                                </div>
                            ))}
                        </section>
                    )}

                    {/* Projects */}
                    {result.projects?.length > 0 && (
                        <section className="mb-5">
                            <h2 className="text-lg font-semibold border-b border-gray-400 pb-1 mb-2 text-gray-800 uppercase tracking-wide">
                                Projects
                            </h2>
                            {result.projects.map((proj, idx) => (
                                <div key={idx} className="mb-3">
                                    <p className="font-semibold text-gray-900">
                                        {proj.name} — <span className="italic">{proj.technologies}</span>
                                    </p>
                                    <p className="text-sm text-gray-700">{proj.description}</p>
                                </div>
                            ))}
                        </section>
                    )}

                    {/* Skills */}
                    {result.skills?.length > 0 && (
                        <section>
                            <h2 className="text-lg font-semibold border-b border-gray-400 pb-1 mb-2 text-gray-800 uppercase tracking-wide">
                                Skills
                            </h2>
                            <p className="text-sm text-gray-700">{result.skills.join(", ")}</p>
                        </section>
                    )}
                </div>

                {/* ===== PDF Download Button ===== */}
                <div className="flex justify-center mt-6">
                    <Button color="primary" onPress={handleDownload}>
                        Download as PDF
                    </Button>
                </div>
            </Card>
        </div>
    );
}

export default ResultPage;
