import { useState, useEffect, useRef } from "react";
import axios from "axios";
import DOMPurify from 'dompurify';
import "./style.scss";

function Home() {
  const baseurl = "https://waterfall-wizards.azurewebsites.net/";
  const divRef = useRef(null);
  const [ques, setQues] = useState();
  const [chats, setHistory] = useState([]);
  const [fileNames, setfileNames] = useState([]);
  const [selectedName, setSelectedName] = useState("");
  const [selectedFileType, setSelectedFileType] = useState("");
  const [summary, setSummary] = useState("");

  const [show, setShow] = useState(false);
  const [files, setFiles] = useState([]);
  const [videoLink, setVideoLink] = useState("");
  const [uploadedResponse, setUploadedResponse] = useState("");

  const handleShow = () => setShow(!show);

  useEffect(() => {
    divRef.current.scrollIntoView({ behavior: "smooth" });
  });

  const handleFileUpload = (event) => {
    setFiles([event.target.files]);
    uploadFileHandler();
  };

  const uploadFileHandler = async () => {
    if (files.length > 0) {
      const formData = new FormData();
      formData.append("file", files[0]);
      try {
        const response = await axios.post(baseurl + "index_document", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
        setUploadedResponse(response.data);
      } catch (e) {
        console.log(e);
      } finally {
        setFiles([]);
        handleShow();
      }
    }
  };

  const handleLinkChange = (event) => {
    setVideoLink(event.target.value);
    if (event.key === "Enter") {
      uploadLinkHandler();
    }
  };

  const uploadLinkHandler = async () => {
    if (videoLink.length > 0) {
      try {
        const response = await axios.post(baseurl +"index_youtubelink?link=" + videoLink, {});
        setUploadedResponse(response.data);
      } catch (e) {
        console.log(e);
      } finally {
        setVideoLink("");
        handleShow();
      }
    }
  };

  const updateQues = (e) => {
    setQues(e.target.value);
  };
  
  const fetchNames = async () => {
    const fullList = await axios.get(baseurl + "get_file_name");
    setfileNames(fullList.data);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      setQues(e.target.value);
      fetchAnswer();
    }
  };

  function askQues() {
    fetchAnswer();
  }

  const handleFileChange = (event) => {
    const fileName = event.target.value;
    setSelectedName(fileName);
    fetchSummary(fileName);
  };

  const fetchSummary = async (file) => {
    const summaryUrl = baseurl + file + "/summary/";
    const currentSummary = await axios.get(summaryUrl);
    setSummary(currentSummary.data);
  };

  const fetchAnswer = async () => {
    const quesSendAt = getSendAt();
    const question = {
      text: ques,
      fileName: selectedName,
    };
    try {
      const response = await axios.post(baseurl + "Query", question);
      const clean = DOMPurify.sanitize(response.data, {USE_PROFILES: {html: true}});
      var chat = [
        { type: "user", response: ques, sendAt: quesSendAt },
        { type: "system", response: clean, sendAt: getSendAt() },
      ];
      setHistory([...chats, ...chat]);
      setQues("");
    } catch (e) {
      console.log(e);
    }
  };

  const getSendAt = () => {
    const date = new Date();
    const hours = date.getHours() % 12 || 12;
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const ampm = hours >= 12 ? "AM" : "PM";
    const timeString = `${hours}:${minutes} ${ampm}`;
    return `${timeString}, Today`;
  };

  const deleteItem = async (fileName) => {
    try {
      await axios.delete(baseurl + `remove_item/${fileName}`);
    } catch (e) {
      console.log(e);
    } finally {
      window.location.reload();
    }
  };

  useEffect(() => {
    fetchNames();
  }, []);

  const ChatHistory = () => {
    return (
      <>
        {chats &&
          chats.map((chat, index) => (
            <div key={index}>
              {chat.type === "user" && (
                <div className="d-flex justify-content-end mb-4">
                  <div className="msg_cotainer_send">
                    {chat.response}
                    <span className="msg_time_send">{chat.sendAt}</span>
                  </div>
                  <div className="img_cont_msg">
                    <img
                      src="../user.png"
                      className="rounded-circle user_img_msg"
                    />
                  </div>
                </div>
              )}
              {chat.type === "system" && (
                <div className="d-flex justify-content-start mb-4">
                  <div className="img_cont_msg">
                    <img
                      src="../chatbot.png"
                      className="rounded-circle user_img_msg"
                    />
                  </div>
                  <div className="msg_cotainer" style={{whiteSpace: "pre-wrap"}}>
                    {
                    chat.response
                    }
                    <span className="msg_time">{chat.sendAt}</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        <div ref={divRef}></div>
      </>
    );
  };

  return (
    <>
    <div className="parent">
      <div className="chat">
      {chats.length === 0 && <div className="Background">
        <div className="Study-Mate">
          StudyMate
        </div>
        <div>
          <img src="../StudyMateLogo.png" className="Background-Logo"/>
        </div>
        <div className="Description">
          Your Daily AI Assistant
        </div>
      </div>}
      <div className='chat-history-conatiner'>
                <ChatHistory />
            </div>
      <div className="Current-File">
        {!selectedName && <label>Please Select a File</label>}
        {selectedName && (
          selectedFileType === "document" ? <div><img src="./document.svg" /><label className="current-file-text">{selectedName}</label></div> : <div><img src="./youtube.svg" /><label className="current-file-text">{selectedName}</label></div>)}
      </div>
      {show && <div className="upload-container">
        <div className="card">
          <ul className="list-group list-group-flush">
            <li className="list-group-item"><input
                          type="file"
                          multiple
                          id="actual-btn"
                          onChange={handleFileUpload}
                          className="file-selector"
                        /></li>
            <li className="list-group-item"><input
                          type="text"
                          value={videoLink}
                          onChange={handleLinkChange}
                          onKeyUp={handleLinkChange}
                          className="form-control"
                          id="videoLink"
                          name="videoLink"
                          placeholder="Paste youtube link"
                        /></li>
          </ul>
        </div>
      </div>}
      <div className="chat-input">
        <div className="Input-Bar">
          <input type="text"
          value={ques} onKeyDown={handleKeyDown} onChange={updateQues}
          placeholder="Upload a video, pdf, image to summerise or ask me anything to start a conversation" 
          className="Input-Query form-control"
          />
          
            <button className="Send-Button" type="button" onClick={askQues}>
              <img src="../Union.png" className="Send-Img" />
            </button>
            <button className="Upload-File-Button" type="button" onClick={handleShow}>
              <img src="../Vector.png" className="Upload-File-Img" />
            </button>
          
        </div>
      </div>
      </div>

    <div className="history">
      <div className="message">
        <strong>Files/Links Uploaded ({fileNames.length})</strong>
        <div className="break bg-light"><hr /></div>
      </div>
      {fileNames && fileNames.map((item) => 
      <>
      <div className="item" style={selectedName === item.name ? {backgroundColor: "lightgray"} : null}>
        <div className='file' key={item.name}>
          <div className="doc-icon">
            {item.fileType === "document" ? <img src="./document.svg" alt="document logo"/> : <img src="./youtube.svg" alt="youtube link logo"/>}
          </div>
          <div
            className="file-name"
            onClick={async () => {
              await fetchSummary(item.name);
              {selectedName !== item.name ? setSelectedName(item.name) : setSelectedName("")}
              {setSelectedFileType(item.fileType)}
            }}
            style={
              selectedName === item.name ? {color: "purple"} : null
            }>
              {item.name}
          </div>
          <img className="trash-bin" alt="trash bin to delete particular file" src="./trash-bin.png" onClick={() => deleteItem(item.name)}></img>
        </div>
        {selectedName === item.name && <div className="summary">{summary}</div>}
      </div>
      </>)}
    </div>
    <div ref={divRef}></div>
    </div>
    </>
  );
}
export default Home;
