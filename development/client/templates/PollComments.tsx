import React from "react";

import {CSRFToken, Context, reverse, templates, useForm} from "@reactivated";

import {css} from "@linaria/core";

import {Layout} from "@client/components/Layout";
import * as forms from "@client/forms";
import * as styles from "@client/styles";

export default (props: templates.PollComments) => {
    const {question} = props;
    const {request} = React.useContext(Context);
    const [comments, setComments] = React.useState(question.comments);
    const form = useForm({form: props.form});
    const title = `${props.question.question_text} comments`;

    const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const formElement = event.currentTarget;
        const formData = new FormData(formElement);

        const response = await fetch(request.path, {
            method: "POST",
            body: formData,
            headers: {
                Accept: "application/json",
            },
        });

        const data = ((await response.json()) as {props: templates.PollComments}).props;

        setComments(data.question.comments);

        if (data.form.errors != null) {
            form.setErrors(data.form.errors);
        } else {
            form.reset();
        }
    };

    return (
        <Layout title={title}>
            <form
                action={request.path}
                method="post"
                className={css`
                    ${styles.verticallySpaced(10)}
                `}
                onSubmit={onSubmit}
            >
                <h1>{title}</h1>
                {comments.length == 0 ? (
                    <p>No comments yet</p>
                ) : (
                    <>
                        {comments.map((comment, index) => (
                            <p key={index}>{comment.comment_text}</p>
                        ))}
                    </>
                )}

                <CSRFToken />

                <h3>Post comment</h3>
                <p>
                    Comments are created using AJAX. However, if you disable JavaScript
                    this form will still work. Try it.
                </p>

                <forms.Fields form={form} />

                <div className={styles.horizontallySpaced}>
                    <forms.Button type="submit">Comment</forms.Button>
                    <forms.ButtonLink
                        href={reverse("poll_detail", {question_id: question.id})}
                    >
                        View poll
                    </forms.ButtonLink>
                </div>
            </form>
        </Layout>
    );
};
